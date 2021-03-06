"""
Model query and navigation API.
"""
from __future__ import unicode_literals
from textx import metamodel_from_str
from textx.editor.parsetree_processor import classified_parsetree_nodes, REFERENCE

grammar = """
Model: things*=Thing packages*=Package;
Package: "package" "{" packages*=Package refs*=Ref mrefs*=MRef "}";
Thing: "thing" name=ID ";";
Ref: "ref" ref=[Thing] ";";
MRef: "mref" refs+=[Thing] ";";
Comment: /\/\/.*/;
"""


model_str = """thing t1;
thing t2;
thing t3;
// comment
package {
 package {
  ref t2; // comment
 }
 ref t1;
 mref t1 t2 t3;
}
"""

def test_classified_parsetree_nodes_denstity_test():

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    current_position = 0
    refcount = 0
    for c,n,pl in classified_parsetree_nodes(model):
        print(c)
        if c==REFERENCE: refcount += 1
        assert n.position >= current_position, "start pos must follow last pos"
        if n.position > current_position:
            separator = model_str[current_position:n.position]
            assert len(separator.strip(' \t\n')) == 0
        current_position = n.position_end

    assert refcount == 5

    assert current_position-1 <= len(model_str), "check total model text length"
    if current_position-1 < len(model_str):
        terminator = model_str[current_position:]
        assert len(terminator.strip(' \t\n')) == 0

