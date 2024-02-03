import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state='auto'
)

st.markdown('<style>div.block-container{padding-top:1.5rem;}</style>', unsafe_allow_html=True)

st.markdown("<p style='font-size: 30px; font-weight: bold;'>Live Feed</p>", unsafe_allow_html=True)

class VideoTransformer(VideoTransformerBase):
    def __init__(self, source_rtsp):
        self.source_rtsp = source_rtsp
        self.vid_cap = None  # Initialize as None

    def setup(self):
        self.vid_cap = cv2.VideoCapture(self.source_rtsp)

    def transform(self, frame):
        if self.vid_cap is None:
            self.setup()

        success, image = self.vid_cap.read()
        if success:
            image = cv2.resize(image, (720, int(720 * (9 / 16))))
            return image
        
tab1, tab2, tab3, tab4 = st.tabs(["Quezon Avenue", "SM North Edsa", "UPS WOW Center", "Magallanes"])

with tab1:
    video_transformer = VideoTransformer("rtsp://admin:admin123@localhost:5540/cam/realmonitor?channel=1&subtype=0")
    webrtc_streamer(
        key="Quezon Avenue",
        video_transformer_factory=lambda: video_transformer,
    )

with tab2:
    video_transformer = VideoTransformer("rtsp://admin:admin123@localhost:5541/cam/realmonitor?channel=1&subtype=0")
    webrtc_streamer(
        key="SM North Edsa",
        video_transformer_factory=lambda: video_transformer,
    )

with tab3:
    video_transformer = VideoTransformer("rtsp://admin:admin123@localhost:5542/cam/realmonitor?channel=1&subtype=0")
    webrtc_streamer(
        key="UPS WOW Center",
        video_transformer_factory=lambda: video_transformer,
    )

with tab4:
    video_transformer = VideoTransformer("rtsp://admin:admin123@localhost:5543/cam/realmonitor?channel=1&subtype=0")
    webrtc_streamer(
        key="Magallanes",
        video_transformer_factory=lambda: video_transformer,
    )

