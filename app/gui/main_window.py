import json
import statistics
import sys
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont,QIcon,QPixmap
from PySide6.QtWidgets import (QApplication,QCheckBox,QFileDialog,QFrame,QGridLayout,QHBoxLayout,QInputDialog,QLabel,
 QMainWindow,QMessageBox,QPlainTextEdit,QPushButton,QScrollArea,QSizePolicy,QVBoxLayout,QWidget)
from app.gui.attempt_fields import AttemptFields
from app.auth.browser import LoginWindow,clear_browser_session
from app.auth.keychain import delete_token,load_token,save_token,storage_error
from app.auth.linux_sandbox import browser_sandbox_available
from app.logging.redaction import mask_token,redact_text
from app.scheduler.clock import SyncedClock,next_beijing_midnight
from app.scheduler.engine import AttemptScheduler
from app.scheduler.dispatcher import ConcurrentAttemptDispatcher
from app.scheduler.adaptive import fire_offsets_ms,latency_stats
from app.xiaomi.client import XiaomiClient,stable_device_id
from app.xiaomi.models import ResultKind
from app.platform_support import AsyncSleepInhibitor,SleepInhibitor,app_data_dir

APPDATA=app_data_dir()

def resource_path(name):
    base=Path(getattr(sys,"_MEIPASS",Path(__file__).parents[2]))
    return base/"assets"/name

STYLE="""
QMainWindow, QWidget { background: #111318; color: #e8eaf0; font-family: "Segoe UI", "SF Pro Text", "DejaVu Sans", sans-serif; font-size: 13px; }
QLabel, QCheckBox { background: transparent; }
QWidget#attemptFields, QWidget#attemptField { background: transparent; }
QFrame#card { background: #191c23; border: 1px solid #292d37; border-radius: 12px; }
QLabel#appTitle { font-size: 25px; font-weight: 700; color: #ffffff; }
QLabel#subtitle { font-size: 12px; color: #8f96a8; }
QLabel#sectionTitle { font-size: 13px; font-weight: 700; color: #f1f2f5; }
QLabel#fieldName { color: #8f96a8; font-size: 12px; }
QLabel#timeValue { color: #ffffff; font-family: Consolas, Menlo, "DejaVu Sans Mono", monospace; font-size: 13px; }
QLabel#sessionBadge { background: #232730; border: 1px solid #343945; border-radius: 9px; padding: 7px 11px; color: #b7bdca; }
QPushButton { background: #282c35; border: 1px solid #393e49; border-radius: 8px; padding: 8px 13px; color: #edf0f5; }
QPushButton:hover { background: #323743; border-color: #505766; }
QPushButton:pressed { background: #20232a; }
QPushButton:disabled { color: #666c78; background: #1c1f25; border-color: #292d34; }
QPushButton#primary { background: #ff6900; border-color: #ff7b22; color: white; font-weight: 700; padding: 10px 18px; }
QPushButton#primary:hover { background: #ff7a1a; }
QPushButton#danger { color: #ff8181; border-color: #67383d; background: #2b2024; }
QPushButton#quiet { background: transparent; border-color: #30343d; color: #aeb4c1; }
QCheckBox { color: #e4e7ed; spacing: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QSpinBox { background: #101217; border: 1px solid #343945; border-radius: 7px; padding: 8px 36px 8px 12px; color: white; font-family: Consolas, Menlo, "DejaVu Sans Mono", monospace; font-size: 14px; }
QSpinBox:focus { border-color: #ff6900; }
QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 24px; border-left: 1px solid #343945; border-bottom: 1px solid #343945; border-top-right-radius: 7px; background: #282c35; }
QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 24px; border-left: 1px solid #343945; border-bottom-right-radius: 7px; background: #282c35; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #424958; }
QPlainTextEdit { background: #0b0d11; border: 1px solid #292d37; border-radius: 10px; padding: 10px; color: #cdd3df; selection-background-color: #78411e; }
"""
STYLE += f'''
QSpinBox::up-arrow {{ image: url("{resource_path("chevron-up.svg").as_posix()}"); width: 12px; height: 8px; }}
QSpinBox::down-arrow {{ image: url("{resource_path("chevron-down.svg").as_posix()}"); width: 12px; height: 8px; }}
'''

class Bridge(QObject):
    log=Signal(str); session=Signal(str); done=Signal(str); ntp=Signal(float,float,str)

class MainWindow(QMainWindow):
    def __init__(self, *, smoke_test=False):
        super().__init__(); self.setWindowTitle("Xiaomi Mi Community Unlock Helper"); self.resize(980,820); self.setMinimumSize(640,460); self.setStyleSheet(STYLE)
        self.clock=SyncedClock(); self.scheduler=AttemptScheduler(self.clock); self.dispatcher=None; self.bridge=Bridge(); self.login_window=None; self.logout_profile=None
        self.prepare_cancel=threading.Event(); self.sleep_inhibitor=AsyncSleepInhibitor() if sys.platform.startswith("linux") else SleepInhibitor(); self.outbound_ms=0.0; self.channels=[]
        self.token="" if smoke_test else load_token() or ""; self.device_id="smoke-test-only" if smoke_test else stable_device_id(APPDATA/"device_id"); self.client=None
        self.offsets=[]; self._build(); self._wire(); self._tick()
        if smoke_test:
            self.ntp_label.setText("Offline build verification")
            for button in (self.login_btn,self.logout_btn,self.paste_btn,self.check_btn,self.start_btn): button.setEnabled(False)
        else:
            if storage_error(): self._log(storage_error())
            self._sync_ntp()
        if self.token: self._set_session(f"● Token stored: {mask_token(self.token)}")
    def _build(self):
        root=QWidget(); outer=QVBoxLayout(root); outer.setContentsMargins(24,22,24,20); outer.setSpacing(14)
        self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.NoFrame); self.scroll.setWidget(root); self.setCentralWidget(self.scroll)
        header=QHBoxLayout(); header.setSpacing(13)
        logo=QLabel(); logo.setFixedSize(56,56); logo.setPixmap(QPixmap(str(resource_path("app-icon-macos.png"))).scaled(56,56,Qt.KeepAspectRatio,Qt.SmoothTransformation)); header.addWidget(logo)
        brand=QVBoxLayout(); brand.setSpacing(2)
        title=QLabel("Xiaomi Mi Community Unlock Helper"); title.setObjectName("appTitle")
        subtitle=QLabel("Precision application scheduler  •  Local-only credentials  •  Beijing time") ; subtitle.setObjectName("subtitle")
        title.setWordWrap(True); subtitle.setWordWrap(True)
        brand.addWidget(title); brand.addWidget(subtitle); header.addLayout(brand,1); outer.addLayout(header)

        account=self._card(); account_layout=QVBoxLayout(account); account_layout.setContentsMargins(16,14,16,14); account_layout.setSpacing(11)
        section=QLabel("ACCOUNT & SESSION"); section.setObjectName("sectionTitle"); account_layout.addWidget(section)
        account_row=QGridLayout(); account_row.setSpacing(8)
        self.login_btn=QPushButton("Add / Login Xiaomi"); self.logout_btn=QPushButton("Logout Xiaomi"); self.paste_btn=QPushButton("Paste Token Manually"); self.check_btn=QPushButton("Check Session")
        self.login_btn.setObjectName("primary"); self.logout_btn.setObjectName("quiet"); self.paste_btn.setObjectName("quiet")
        for index,button in enumerate((self.login_btn,self.logout_btn,self.paste_btn,self.check_btn)): account_row.addWidget(button,index//2,index%2)
        account_layout.addLayout(account_row)
        self.session_label=QLabel("○ No token"); self.session_label.setObjectName("sessionBadge"); account_layout.addWidget(self.session_label)
        outer.addWidget(account)

        timing=self._card(); timing_layout=QVBoxLayout(timing); timing_layout.setContentsMargins(16,14,16,14); timing_layout.setSpacing(11)
        section=QLabel("CLOCK & QUOTA WINDOW"); section.setObjectName("sectionTitle"); timing_layout.addWidget(section)
        grid=QGridLayout(); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(8); timing_layout.addLayout(grid)
        self.local_label=QLabel(); self.bj_label=QLabel(); self.ntp_label=QLabel("syncing…"); self.reset_label=QLabel(); self.count_label=QLabel()
        labels=[("Local Time:",self.local_label),("Beijing Time:",self.bj_label),("NTP Offset / RTT:",self.ntp_label),("Quota Reset:",self.reset_label),("Countdown:",self.count_label)]
        for row,(name,val) in enumerate(labels):
            field=QLabel(name); field.setObjectName("fieldName"); val.setObjectName("timeValue"); grid.addWidget(field,row,0); grid.addWidget(val,row,1)
            if row<2: grid.addWidget(QWidget(),row,2)
        grid.setColumnStretch(1,1); outer.addWidget(timing)

        execution=self._card(); execution_layout=QVBoxLayout(execution); execution_layout.setContentsMargins(16,14,16,14); execution_layout.setSpacing(12)
        top=QHBoxLayout(); section=QLabel("ADAPTIVE EXECUTION"); section.setObjectName("sectionTitle"); top.addWidget(section); top.addStretch()
        self.adaptive=QCheckBox("Adaptive server-arrival timing"); self.adaptive.setChecked(True); top.addWidget(self.adaptive); execution_layout.addLayout(top)
        hint=QLabel("Desired arrival at Xiaomi server, relative to Beijing midnight"); hint.setObjectName("subtitle"); hint.setWordWrap(True); execution_layout.addWidget(hint)
        self.attempt_fields=AttemptFields(); self.offset_spins=self.attempt_fields.spins
        execution_layout.addWidget(self.attempt_fields)
        controls=QHBoxLayout(); self.start_btn=QPushButton("START WAITING (LIVE)"); self.cancel_btn=QPushButton("EMERGENCY CANCEL"); self.cancel_btn.setEnabled(False)
        self.start_btn.setObjectName("primary"); self.cancel_btn.setObjectName("danger"); controls.addStretch(); controls.addWidget(self.cancel_btn); controls.addWidget(self.start_btn); execution_layout.addLayout(controls); outer.addWidget(execution)

        log_header=QHBoxLayout(); log_title=QLabel("ACTIVITY LOG"); log_title.setObjectName("sectionTitle"); log_header.addWidget(log_title); log_header.addStretch(); outer.addLayout(log_header)
        self.logbox=QPlainTextEdit(); self.logbox.setReadOnly(True); self.logbox.setFont(QFont("Consolas" if sys.platform=="win32" else "Menlo" if sys.platform=="darwin" else "DejaVu Sans Mono",11)); self.logbox.setMinimumHeight(120); outer.addWidget(self.logbox,1)
        logbuttons=QHBoxLayout(); self.copy_btn=QPushButton("Copy Log"); self.save_btn=QPushButton("Save Log"); self.clear_btn=QPushButton("Clear Log")
        for b in (self.copy_btn,self.save_btn,self.clear_btn): b.setObjectName("quiet"); logbuttons.addWidget(b)
        logbuttons.addStretch(); outer.addLayout(logbuttons)
    def _card(self):
        card=QFrame(); card.setObjectName("card"); card.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum); return card
    def _wire(self):
        self.bridge.log.connect(self._log); self.bridge.session.connect(self._set_session); self.bridge.done.connect(self._finished); self.bridge.ntp.connect(lambda o,d,s:self.ntp_label.setText(f"{o*1000:+.3f} ms / {d*1000:.1f} ms ({s})"))
        self.login_btn.clicked.connect(self.login); self.logout_btn.clicked.connect(self.logout); self.paste_btn.clicked.connect(self.paste); self.check_btn.clicked.connect(self.check_session); self.start_btn.clicked.connect(self.start); self.cancel_btn.clicked.connect(self.cancel)
        self.copy_btn.clicked.connect(lambda:QApplication.clipboard().setText(self.logbox.toPlainText())); self.clear_btn.clicked.connect(self.logbox.clear); self.save_btn.clicked.connect(self.save_log)
        timer=QTimer(self); timer.timeout.connect(self._tick); timer.start(50); self.timer=timer
    def _log(self,msg): self.logbox.appendPlainText(f"[{self.clock.beijing_now().strftime('%H:%M:%S.%f')[:-3]}] {redact_text(msg)}")
    def _set_session(self,text):
        self.session_label.setText(text)
        good=text.startswith("●") and not any(x in text for x in ("EXPIRED","INVALID","BLOCKED","ERROR"))
        self.session_label.setStyleSheet("color:#70df91; border-color:#285c3b; background:#17281f;" if good else "")
    def _tick(self):
        now=datetime.now().astimezone(); bj=self.clock.beijing_now(); reset=next_beijing_midnight(self.clock); delta=max(0,(reset-bj).total_seconds())
        self.local_label.setText(now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]); self.bj_label.setText(bj.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]+" GMT+8")
        self.reset_label.setText(reset.strftime("%Y-%m-%d 00:00:00 GMT+8")); h=int(delta)//3600; m=(int(delta)%3600)//60; s=delta%60; self.count_label.setText(f"{h:02}:{m:02}:{s:06.3f}")
    def _sync_ntp(self):
        def work():
            try:
                x=self.clock.sync(); self.bridge.ntp.emit(x.offset,x.delay,x.server); self.bridge.log.emit("NTP sync OK")
            except Exception as e: self.bridge.log.emit(f"NTP sync failed; system clock fallback: {e}")
        threading.Thread(target=work,daemon=True).start()
    def login(self):
        if not browser_sandbox_available():
            QMessageBox.warning(self,"Browser sandbox unavailable",
                "Linux blocked the browser sandbox. Run the app as your normal desktop user. "
                "On Ubuntu 24.04, the Linux package includes an optional enable-browser-sandbox.sh helper. "
                "You can also use Paste Token Manually.")
            return
        self.login_window=LoginWindow(APPDATA/"browser-profile"); self.login_window.token_found.connect(self._browser_token); self.login_window.show(); self._log("Opened isolated Xiaomi login profile; password remains inside Xiaomi's page")
    def logout(self):
        self.prepare_cancel.set(); self.scheduler.cancel()
        if self.dispatcher: self.dispatcher.cancel(); self.dispatcher.shutdown(); self.dispatcher=None
        self._stop_caffeinate()
        if self.login_window: self.login_window.close(); self.login_window.deleteLater(); self.login_window=None
        deleted=delete_token(); self.token=""; self.client=None; self.channels=[]
        self.logout_profile=clear_browser_session(APPDATA/"browser-profile",self)
        self._set_session("○ No token — logged out")
        self.start_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
        self._log("Logged out: saved token and isolated browser session cleared" if deleted else storage_error())
    @Slot(str)
    def _browser_token(self,token):
        self.token=token; saved=save_token(token); self._set_session(f"● Token captured: {mask_token(token)}"); self._log(f"new_bbs_serviceToken={token}")
        if not saved: self._log(storage_error())
        QTimer.singleShot(100,self.check_session)
    def paste(self):
        token,ok=QInputDialog.getText(self,"Paste Token","new_bbs_serviceToken:")
        if ok and token.strip(): self._browser_token(token.strip())
    def _get_client(self):
        if not self.token: raise RuntimeError("No token — login or paste token first")
        if not self.client or self.client.token!=self.token: self.client=XiaomiClient(self.token,self.device_id)
        return self.client
    def check_session(self):
        def work():
            try:
                result,ms=self._get_client().check_state(); self.bridge.session.emit(f"● {result.kind.value}: {result.message}"); self.bridge.log.emit(f"Session: {result.kind.value} ({ms:.1f} ms); raw={result.raw}")
            except Exception as e: self.bridge.log.emit(str(e))
        threading.Thread(target=work,daemon=True).start()
    def start(self):
        try: client=self._get_client()
        except Exception as e: QMessageBox.warning(self,"Cannot start",str(e)); return
        self.start_btn.setEnabled(False); self.cancel_btn.setEnabled(True); arrival_offsets=[s.value() for s in self.offset_spins]; mode="LIVE"
        self.prepare_cancel.clear(); self._start_caffeinate()
        self._log(f"Adaptive preparation armed ({mode}); desired server arrivals: {arrival_offsets} ms relative to midnight")
        threading.Thread(target=self._prepare_and_arm,args=(client,arrival_offsets,mode,self.adaptive.isChecked()),daemon=True).start()

    def _prepare_and_arm(self,client,arrival_offsets,mode,adaptive):
        try:
            midnight=next_beijing_midnight(self.clock)
            seconds=(midnight-self.clock.beijing_now()).total_seconds()
            # Re-synchronize near the precision window without blocking the GUI.
            if seconds>75 and self.prepare_cancel.wait(seconds-65): return
            try:
                sample=self.clock.sync(samples=1); self.bridge.ntp.emit(sample.offset,sample.delay,sample.server)
                self.bridge.log.emit("Final NTP sync OK")
            except Exception as e: self.bridge.log.emit(f"Final NTP sync failed; retained previous clock: {e}")
            if self.prepare_cancel.is_set(): return
            samples=[]
            for _ in range(5):
                result,ms=client.check_state(); samples.append(ms)
                if result.kind in (ResultKind.EXPIRED,ResultKind.INVALID): raise RuntimeError(result.message)
            stats=latency_stats(samples); self.outbound_ms=stats.outbound_ms
            self.bridge.log.emit(f"Latency calibration: RTT median {stats.median_ms:.1f} ms, p90 {stats.p90_ms:.1f} ms, jitter {stats.jitter_ms:.1f} ms; estimated outbound {stats.outbound_ms:.1f} ms")
            self.channels=[client.new_channel() for _ in arrival_offsets]
            warm=[]; threads=[]
            def warm_one(channel):
                _,ms=channel.check_state(); warm.append(ms)
            for channel in self.channels:
                t=threading.Thread(target=warm_one,args=(channel,),daemon=True); threads.append(t); t.start()
            for t in threads: t.join(5)
            if warm:
                stats=latency_stats(warm); self.outbound_ms=stats.outbound_ms
                self.bridge.log.emit(f"4-channel warm-up complete; RTT median {stats.median_ms:.1f} ms; outbound estimate {self.outbound_ms:.1f} ms")
            offsets=fire_offsets_ms(arrival_offsets,self.outbound_ms) if adaptive else [1400,900,400,100]
            self.bridge.log.emit(f"Scheduler armed ({mode}); computed fire offsets before midnight: {[round(x,1) for x in offsets]} ms")
            self._arm_scheduler(client,arrival_offsets,offsets,midnight)
        except Exception as e:
            self.bridge.log.emit(f"Unable to arm scheduler: {e}"); self.bridge.done.emit("Scheduler preparation failed")

    def _arm_scheduler(self,client,arrival_offsets,offsets,midnight):
        def log_fire(a):
            target=datetime.fromtimestamp(a.target_wall,timezone(timedelta(hours=8))); actual=datetime.fromtimestamp(a.actual_wall,timezone(timedelta(hours=8)))
            estimated_arrival=a.actual_wall+self.outbound_ms/1000
            arrival=datetime.fromtimestamp(estimated_arrival,timezone(timedelta(hours=8)))
            self.bridge.log.emit(f"Attempt #{a.number} fired | Target {target.strftime('%H:%M:%S.%f')} | Actual {actual.strftime('%H:%M:%S.%f')} | Error {a.error_ms:+.3f} ms | Estimated server arrival {arrival.strftime('%H:%M:%S.%f')}")
        def fired(a):
            log_fire(a)
            return self.dispatcher.submit(a)
        def request_work(a):
            channel=self.channels[a.number-1] if self.channels else client
            result,ms=channel.apply()
            return result,ms
        def request_result(a,packed):
            result,ms=packed
            self.bridge.log.emit(f"Attempt #{a.number} response: {result.kind.value} ({ms:.1f} ms); {result.message}; deadline={result.deadline}; raw={result.raw}")
            if result.verify:
                threading.Event().wait(1.5); state,vms=client.check_state(); self.bridge.log.emit(f"Post-request verification: {state.kind.value} ({vms:.1f} ms); {state.message}; deadline={state.deadline}; raw={state.raw}")
        def dispatch_done(packed):
            result=packed[0] if packed else None
            self.bridge.done.emit(result.kind.value if result else "All 4 request responses received")
        if client:
            self.dispatcher=ConcurrentAttemptDispatcher(len(offsets),request_work,request_result,
                lambda packed: packed[0].terminal,self.scheduler.cancel,dispatch_done)
        self.scheduler.start(offsets,fired,midnight)
    def cancel(self):
        self.prepare_cancel.set()
        self.scheduler.cancel()
        if self.dispatcher: self.dispatcher.cancel()
        self._log("Emergency cancel requested; in-flight HTTP requests may still finish")
        self._finished("Cancelled")
    def _finished(self,text): self._stop_caffeinate(); self.start_btn.setEnabled(True); self.cancel_btn.setEnabled(False); self._log(text)
    def _start_caffeinate(self):
        if isinstance(self.sleep_inhibitor,AsyncSleepInhibitor): self.sleep_inhibitor.start(self.bridge.log.emit)
        elif self.sleep_inhibitor.start(): self._log("Sleep prevention enabled")
        else: self._log("Sleep prevention unavailable — keep the computer awake while waiting")
    def _stop_caffeinate(self):
        self.sleep_inhibitor.stop()
    def closeEvent(self,event):
        self.prepare_cancel.set(); self.scheduler.cancel()
        if self.dispatcher: self.dispatcher.cancel(); self.dispatcher.shutdown()
        self._stop_caffeinate(); super().closeEvent(event)
    def save_log(self):
        path,_=QFileDialog.getSaveFileName(self,"Save redacted log",str(Path.home()/"Desktop/xiaomi-unlock-helper.log"),"Log (*.log);;Text (*.txt)")
        if path: Path(path).write_text(redact_text(self.logbox.toPlainText()))
