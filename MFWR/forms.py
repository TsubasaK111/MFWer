from wtforms import Form, BooleanField, StringField, DateField, IntegerField, DecimalField, validators

class MFWForm(Form):
    MFW_name =          StringField( "Name",
                                 [ validators.InputRequired(),
                                   validators.Length(min=2, max=20) ] )
    MFW_description =   StringField( "Description",
                                 [ validators.InputRequired(),
                                   validators.Length(min=2, max=100) ] )
    id =            IntegerField( "MFW_ID" )
    image_url =     StringField( "Image URL", [validators.URL() ] )
    reference_url = StringField( "Reference URL", [ validators.URL() ] )


class ElementForm(Form):
    letter =      StringField( "Letter",
                               [ validators.InputRequired(),
                                 validators.Length(min=1, max=1) ] )
    description = StringField( "Description",
                               [ validators.InputRequired(),
                                 validators.Length(min=2, max=100) ] )
    order =       IntegerField("Order",
                               [ validators.InputRequired() ] )
    id =          IntegerField("element_ID" )
