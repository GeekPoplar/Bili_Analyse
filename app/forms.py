from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

class Video_Url_Form(FlaskForm):
    url=StringField('请输入你要分析的视频的链接',validators=
                    [DataRequired()])
    submit=SubmitField('点击分析')