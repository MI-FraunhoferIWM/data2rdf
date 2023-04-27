# The csv2rdf conversion requires a set of relations and classes to use for
# the annotation these are defined separately, so that they can be easily
# adapted.

annotations = {
    # EMMO classes and relations
    "quantity_class": "http://emmo.info/emmo/middle/metrology#EMMO_f658c301_ce93_46cf_9639_4eace2c5d1d5",  # Quantity
    "numeric_class": "http://emmo.info/emmo/middle/math#EMMO_4ce76d7f_03f8_45b6_9003_90052a79bfaa",  # Numeric
    "meta_data_value_annotation": "http://emmo.info/emmo/middle/perceptual#EMMO_23b579e1_8088_45b5_9975_064014026c42",  # hasSymbolData
    "meta_data_quantity_annotation": "http://emmo.info/emmo/middle/metrology#EMMO_8ef3cd6d_ae58_4a8d_9fc0_ad8f49015cd0",  # hasQuantityValue
    # hasNumericalData (needs additional steps since EMMO uses classes to
    # define the data type)
    "meta_data_numeric_annotation": "http://emmo.info/emmo/middle/math#EMMO_faf79f53_749d_40b2_807c_d34244c192f4",
    # hasReferenceUnit (object relation -> unit must be an individual)
    "meta_data_unit_annotation": "http://emmo.info/emmo/middle/metrology#EMMO_67fc0a36_8dcb_4ffa_9a43_31074efa3296",
    # EMMO data model
    "meta_data_type": "http://emmo.info/datamodel#Metadata",  # TODO check metadata class
    # TODO check best way to connect meta data to a dcat file
    "hasMetaData": "http://emmo.info/datamodel#composition",
    # https://github.com/emmo-repo/datamodel-ontology/blob/master/metamodel.ttl
    "column_class": "http://emmo.info/datamodel#DataInstance",
    # Custom class
    "UnitLiteral": "http://emmo.info/emmo/middle/metrology#UnitLiteral",  # TODO add to emmo
}
