from __future__ import unicode_literals

from os.path import dirname, abspath, join

from pytest import raises

import textx.scoping as scoping
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file


def test_exception_from_included_model():
    """
    This test checks that an error induced by an included model
    (thrown via an object processor) is (a) thrown and (b) indicates the
    correct model location (file, line and col).
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": provider,
            "Call.method": scoping_providers.ExtRelativeName("obj.ref",
                                                             "methods",
                                                             "extends")
        })

        def my_processor(m):
            from textx.exceptions import TextXSemanticError
            from textx.scoping.tools import get_location
            if m.name == "d1":
                raise TextXSemanticError("d1 triggers artifical error",
                                         **get_location(m))

        mm.register_obj_processors({"Method": my_processor})
        return mm

    import_lookup_provider = scoping_providers.FQNImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING / TEST
    #################################
    import textx.exceptions

    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*model_d\.b:5:3:.*d1 triggers artifical error'):
        a_mm.model_from_file(
            this_folder + "/metamodel_provider3/inheritance2/model_a.a")

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()
