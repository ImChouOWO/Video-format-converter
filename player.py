import sys
import os
from PyQt5.QtWidgets import QCheckBox,QHBoxLayout,QLineEdit,QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,QComboBox ,QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIntValidator
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl,Qt
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import Gst, GstPbutils, GLib,GObject

class Gstreamer:
    
    def __init__(self,pipeline,speed):
        self.pipeline = pipeline
        self.speed = speed
        self.gsinit = Gst.init(None)
        self.loop = GLib.MainLoop()
        
        

        self.bus =  self.pipeline.get_bus()
        

    def set_bus(self):
        self.bus.add_signal_watch()
        self.bus.connect("message",self.on_msg,self.loop)

    

    def on_msg(self, bus, message, loop):
        mtype = message.type
        if mtype == Gst.MessageType.EOS:
            print("stream end")
            loop.quit()  # 使用传递进来的 loop 参数
        elif mtype == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, {debug}")
            loop.quit()
    def set_speed(self):
        videorate = self.pipeline.get_by_name("myvideorate")
        if videorate:
            videorate.set_property("rate", float(self.speed))

    def start(self):
        try:
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.get_state(Gst.CLOCK_TIME_NONE) 
            self.set_speed()
            self.pipeline.set_state(Gst.State.PLAYING)

            self.loop.run()
        except Exception as e:
            print(f"Exception in running loop: {e}")
            self.pipeline.set_state(Gst.State.NULL)

    def show_text(self,textOverlay):
        textOverlay.set_property('text', 'Hello World 2222')
        return False
    def hide_text(self,textOverlay):
        textOverlay.set_property('text', '')
        return False  
    

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt Video Player')
        self.setGeometry(600, 600, 600, 600)
        self.initUI()
        self.speed = 1
        self.filePath = None
        self.toFormat = None
        self.encode = None
        self.subFileName = None

    def initUI(self):
        # 創建媒體播放器物件
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # 播放按鈕
        self.playButton = QPushButton('格式轉換')
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.playVideo)
        # 檔案選擇按鈕
        self.openButton = QPushButton('打開檔案')
        self.openButton.clicked.connect(self.openFile) 

        #file extention drop down menu
        self.combobox = QComboBox(self)
        self.combobox.addItem("select decoder")
        self.combobox.addItem("mp4","mp4mux")
        self.combobox.addItem("mov","qtmux")
        self.combobox.currentTextChanged.connect(self.comboboxOnchange)
        self.combobox.setEnabled(False)


        # encoder drop down menu
        self.encodeCombobox = QComboBox(self)
        self.encodeCombobox.addItem("select encoder","")
        self.encodeCombobox.addItem("H264","x264enc")
        self.encodeCombobox.currentTextChanged.connect(self.encodeOnchange)
        self.encodeCombobox.setEnabled(False)

        #check box
        self.check_box = QCheckBox(self)
        self.check_box.setEnabled(False)
        self.check_box.stateChanged.connect(self.onStateChanged)

        #input bar
        self.speed_combobox = QComboBox(self)
        self.speed_combobox.addItem("select video speed")
        self.speed_combobox.addItem("x0.25",0.25)
        self.speed_combobox.addItem("x0.5",0.5)
        self.speed_combobox.addItem("x0.75",0.75)
        self.speed_combobox.addItem("x1",1)
        self.speed_combobox.addItem("x1.25",1.25)
        self.speed_combobox.addItem("x1.5",1.5)
        self.speed_combobox.addItem("x1.75",1.75)
        self.speed_combobox.addItem("x2",2)
        self.speed_combobox.setEnabled(False)
        self.speed_combobox.currentTextChanged.connect(self.speedSelect)
     

    

        #speed_layout
        self.speed_layout = QHBoxLayout()
        self.speed_layout.addWidget(self.check_box)
        self.speed_layout.addWidget(self.speed_combobox)

        info_layout = QHBoxLayout()

        #text lable
        self.label = QLabel("")

        #media compoment
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        info_layout.addWidget(self.label)
        info_layout.addWidget(self.videoWidget)

        # layout set up
        layout = QVBoxLayout()
        layout.addLayout(info_layout)
        layout.addWidget(self.label)
        layout.addWidget(self.openButton)
        layout.addWidget(self.playButton)
        layout.addLayout(self.speed_layout)
        layout.addWidget(self.combobox)
        layout.addWidget(self.encodeCombobox)
        self.setLayout(layout)
       
    def onStateChanged(self, state):
        if state == Qt.Checked:
            self.speed_combobox.setEnabled(True)
        
        else:
            self.speed_combobox.setEnabled(False)
            self.speed = 1
            print(self.speed)
   

    def comboboxOnchange(self,text):

        index = self.combobox.currentIndex()
        self.toFormat = self.combobox.itemData(index)
        self.subFileName = text
        self.checker()
    
    def speedSelect(self,text):
        index = self.speed_combobox.currentIndex()
        self.speed = self.speed_combobox.itemData(index)
        print(self.speed)




    def encodeOnchange(self,text):
        index = self.encodeCombobox.currentIndex()
        self.encode = self.encodeCombobox.itemData(index)
        self.checker()
        
    def file_info(self,path):
        Gst.init(None)


        discoverer = GstPbutils.Discoverer.new(5*Gst.SECOND)
        uri = Gst.filename_to_uri(path)
        info  = discoverer.discover_uri(uri)

        video_info = info.get_video_streams()[0]
        self.resolution = video_info.get_width(), video_info.get_height()
        self.fps = video_info.get_framerate_num() / video_info.get_framerate_denom()
        self.codec = video_info.get_caps().to_string().split()
        self.encoder =self.codec[0].split("/")[1]

        # get file extention
        _, self.file_extension = os.path.splitext(path)

        print(f"file path:{path}")
        print(f"Resolution: {self.resolution}")
        print(f"FPS: {self.fps}")
        print(f"encoder: {self.encoder}")
        print(f"all info:{self.codec}")
        print(f"file extention:{self.file_extension}")

    def set_media(self,filePath):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))
        self.mediaPlayer.play()    

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "選擇媒體檔案", ".", "視頻檔案 (*.mp4 *.avi *.mkv)")

        if filePath != '':
            self.file_info(filePath)
            self.encodeCombobox.setEnabled(True)
            self.combobox.setEnabled(True)
            self.check_box.setEnabled(True)

            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))  # 使用QUrl对象设置媒体内容
            self.mediaPlayer.play()  # 播放视频
            self.mediaPlayer.pause()
            
            self.label.setText(
                f"<div style='margin: 5px 0; padding: 5px;'><font size='6'>副檔名: {self.file_extension}</font></div>"
                f"<div style='margin: 5px 0; padding: 5px;'><font size='6'>FPS: {self.fps}</font></div>"
                f"<div style='margin: 5px 0; padding: 5px;'><font size='6'>解析度: {self.resolution[0]}X{self.resolution[1]}</font></div>"
                f"<div style='margin: 5px 0; padding: 5px;'><font size='6'>編碼格式: {self.encoder[:-1]}</font></div>"
            )

            self.checker()
            self.filePath = filePath
      
            



    def checker(self):
        if self.encode != None and self.toFormat != None and self.subFileName != None and self.filePath != None :
            self.playButton.setEnabled(True)
        else:
            return
   

    def playVideo(self):
        Gst.init(None)
        pipeline = Gst.parse_launch(
        f"filesrc location={self.filePath} ! "
        "decodebin ! "
        "videorate name=myvideorate ! "  # 給 videorate 元件指定名字
        "video/x-raw,framerate=60/1 ! "  # 直接在管道中設置期望的幀率，這裡假設你想要雙倍速度
        "videoscale ! "
        "videoconvert ! "
        "textoverlay name=overlay valignment=top halignment=left color=0xFF0000FF font-desc='Sans, 36'  xpad=10 ypad=10 ! "
        "videoconvert ! "
        f"{self.encode} ! "
        f"{self.toFormat} ! "
        f"filesink location=/Users/zhouchenghan/python/Gstreamer/src/output/convert.{self.subFileName}"
    )
        gstreamer = Gstreamer(pipeline, self.speed)
        gstreamer.set_bus()
        gstreamer.start()

  

           
     



if __name__ == '__main__':
    app = QApplication(sys.argv)
   
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())