from flask_wtf import FlaskForm
from wtforms import StringField, RadioField


# If we put steamKey and analysisType in the same class, it fucks up for some reason
class SteamKeyForm(FlaskForm):
    steamKey = StringField("Steam Key")
    analysisType = RadioField("Radio Buttons", choices=[("combined", "Combined"), ("speed", "Speed"), ("coin", "Coin"),
                                                        ("dark", "Dark")], default="combined")
