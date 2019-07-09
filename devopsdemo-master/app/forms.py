from flask_wtf import FlaskForm,Form
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField, \
                    PasswordField, ValidationError, RadioField,FileField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileRequired,  FileAllowed
from app import db
import pymysql
pymysql.install_as_MySQLdb()
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class SignupForm(Form):
    firstname = StringField('First name', validators=[DataRequired("Please enter your first name.")])
    lastname = StringField('Last name', validators=[DataRequired("Please enter your last name.")])
    email = StringField('Email', validators=[DataRequired("Please enter your email address."),
                                             Email("Please enter your email address.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter a password."),
                                                     EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired("Please enter your email address."),
                                             Email("Please enter your email address.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter a password.")])
    remember_me = BooleanField('remember_me', default=False)

class OperationsForm(Form):
    do_action = StringField('Action')
    hostname = StringField('Hostname', validators=[DataRequired()])
    cmd = StringField('Command', validators=[DataRequired()])

class RacktablesForm(Form):
    do_action = StringField('Action')
    objectname = StringField('Object Name')
    objecttype_choices = [('online_mode','Online Mode'),
                          ('offline_mode','Offline Mode'),
                          ('patch_panel','Patch Panel'),
                          ('network_switch','Network Switch'),
                          ('pdu','PDU'),
                          ('network_security','Network Security')]
    objecttype = RadioField('Object Type', choices=objecttype_choices)
    rackspace = StringField('Rackspace')
    rackposition_choices = [('none','rackposition'),
                            ('left','left'),('right','right'),
                            ('front','front'),('interior','interior'),('back','back')]
    rackposition = SelectField('Rackposition',choices=rackposition_choices)

class EditorForm(Form):
    do_action = StringField('Action')
    file_path = StringField('File Path', validators=[DataRequired()])
    file_data = TextAreaField('File Data')

class HadoopForm(Form):
    do_action = StringField('Action')
    slave_hostname = StringField('Slave Hostname')
    choices = [('none','master_hostname'),
               ('idc1-hnn1','idc1-hnn1'),('idc2-hnn1','idc2-hnn1'),
               ('idc1-hrm1','idc1-hrm1'),('idc2-hrm1','idc2-hrm1')]
    master_hostname = SelectField('Master Hostname',choices=choices)


class UploadForm(FlaskForm):
    """用户上传文件的表单"""
    file = FileField(
        label="格式为.mat",
        validators=[
            # 文件必须选择;
            FileRequired(),
            # 指定文件上传的格式;
            FileAllowed([ "mat"], '只接收.pdf和.txt格式的简历')
        ]
    )

    submit = SubmitField(
        render_kw={
            'value': "上传",
            'class': 'btn btn-success pull-right'
        }
    )
