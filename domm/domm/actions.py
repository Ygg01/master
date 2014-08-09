from arpeggio import SemanticAction
from metamodel import *

class DommAction(SemanticAction):
    """
    Simple action that returns a dictionary of models
    """
    def first_pass(self, parser, node, children):
        model_map = dict()

        filter_children = (x for x in children if type(x) != str)

        for x in filter_children:
            model_map[x.name] = x
        return model_map

class ModelAction(SemanticAction):
    """
    Represents semantic action Model in DOMMLite
    """
    def first_pass(self, parser, node, children):
        # ID should been always present
        model = Model()

        for ind, val in enumerate(children):
            if type(val) is Id:
                model.name = val._id
            elif type(val) is NamedElement:
                model.set_desc(val.short_desc, val.long_desc)
            elif type(val) is DataType or type(val) is Enumeration:
                model.add_type(val)
            elif type(val) is Constraint:
                model.add_constraint(val)
            elif type(val) is Package:
                model.add_package(val)

        if parser.debugDomm:
            print("DEBUG ModelAction returns: ", model)

        return model

class NamedElementAction(SemanticAction):
    """
    Represents the named element meta class of
    DOMMLite's model. Named elements have long
    and short descriptions
    """
    def first_pass(self, parser, node, children):
        retVal = None

        # Remove all `"`from characters from list of children in case it isn't
        # omitted by the parser
        filter_children = (x for x in children if x != '"' )

        if parser.debugDomm:
            print("Debug NamedElementAction (children)", children)

        for ind, val in enumerate(filter_children):
            if val is not None:
                if not retVal:
                    retVal = NamedElement()

                if ind == 0:
                    retVal.short_desc = val
                else:
                    retVal.long_desc = val
        if parser.debugDomm:
            print("Debug NamedElementAction returns ", retVal)

        return retVal



class StringAction(SemanticAction):
    """
    Represents the basic string identified in programm
    """
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("Debug StringAction (children)", children)

        return children[0]

class IdAction(SemanticAction):
    """
    Represents actions done when identifier is found
    """
    def first_pass(self, parser, node, children):
        return Id(node.value, namespace = parser.namespace)

class IntAction(SemanticAction):
    """
    Returns an integer represenetation
    """
    def first_pass(self, parser, node, children):
        return int(node.value)

class EnumAction(SemanticAction):
    """
    Evaluates value of enumeration
    """
    def first_pass(self, parser, node, children):
        enum = Enumeration()

        for val in children:
            if type(val) is Id:
                enum.name = val._id
            elif type(val) is NamedElement:
                enum.set_from_named(val)
            elif type(val) is EnumLiteral:
                enum.add_literal(val)

        enum.set_namespace(parser.namespace)

        return enum

class CommonTagAction(SemanticAction):
    """
    Evaluates value of (buildin)validatorType/tagType
    """
    def first_pass(self, parser, node, children):
        tag = CommonTag()

        if parser.debugDomm:
            print("DEBUG CommonTagAction children: ", children)

        for value in children:
            if type(value) is Id:
                tag.name = value._id
            elif type(value) is ConstrDef:
                tag.constr_def = value
            elif type(value) is ApplyDef:
                tag.applies = value
            elif type(value) is NamedElement:
               tag.set_from_named(value)


        if parser.debugDomm:
            print("DEBUG CommonTagAction returns: ", tag)
        return tag

class ApplyDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        app_def = ApplyDef()

        if parser.debugDomm:
            print("DEBUG ApplyDefAction children: ", children)

        filter_children = (x for x in children if x != "appliesTo")

        for val in children:
            app_def.add_apply(val)

        if parser.debugDomm:
            print("DEBUG ApplyDefAction returns: ", app_def)
        return app_def

class ConstrDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        constr_def = ConstrDef()

        if parser.debugDomm:
            print("DEBUG ConstrDefAction children: ", children)

        # Filter all irrelevant strings from query
        filter_children = (x for x in children if x != "(" and x != ")" and x != ',')

        for val in filter_children:
            constr_def.add_constr(val)

        return constr_def

class EnumLiteralAction(SemanticAction):
    """
    Evaluates value of a part of enumeration
    """
    def first_pass(self, parser, node, children):
        # Name and value are mandatory and will always be present
        # children[0] is the enumeration literal's value
        # children[1] is the enumeration literal's value
        literal =  EnumLiteral(children[0]._id, children[1])

        # Enumeration may have a named element
        if len(children) == 3:
            literal.short_desc = children[2].short_desc
            literal.long_desc = children[2].long_desc

        return literal



class DataTypeAction(SemanticAction):
    """
    Returns evaluated DataType
    """
    def __init__(self, built_in = False):
        self.built_in = built_in

    def first_pass(self, parser, node, children):
        data_type = DataType(built_in = self.built_in)

        if parser.debugDomm:
            print("DEBUG DataTypeAction entered (children): ", children)

        for val in children:
            if type(val) is NamedElement:
                if parser.debugDomm:
                    print("DEBUG DataTypeAction entered (val): ", val)
                data_type.set_from_named(val)
            elif type(val) is Id:
                data_type.name = val._id

        if parser.debugDomm:
            print("DEBUG DataTypeAction returns: ", data_type)

        data_type.set_namespace(parser.namespace)

        return data_type


class ElipsisAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG ElipsisAction called")
        return "..."

class ConstraintAction(SemanticAction):
    """
    Returns evaluated constraint type
    """
    def __init__(self, built_in = False, is_tag = False):
        self.built_in = built_in
        if is_tag:
            self.constr_type = ConstraintType.Tag
        else:
            self.constr_type = ConstraintType.Validator

    def first_pass(self, parser, node, children):
        constraint = Constraint(built_in = self.built_in, constr_type = self.constr_type)

        if parser.debugDomm:
            print("DEBUG ConstraintAction entered children: ", children)

        for i in children:
            if type(i) is CommonTag:
                constraint.tag = i
            elif type(i) is Id:
                constraint.name = i._id

        constraint.set_namespace(parser.namespace)

        if parser.debugDomm:
            print("DEBUG ConstraintAction returns: ", constraint)

        return constraint

class PackageAction(SemanticAction):
    def first_pass(self, parser, node, children):
        package = Package()

        filter_children = (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG PackageAction (children)", children)

        for val in filter_children:
            if type(val) is Id:
                package.set_name(val._id)
            elif type(val) is NamedElement:
                package.set_desc(short_desc = val.short_desc, long_desc = val.long_desc)
            else:
                package.add_elem(val)

        return package

class TypeDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        type_def = TypeDef()

        for ind, val in enumerate(children):
            if type(val) is Id and ind == 0:
                type_def.set_type(val._id)
            elif type(val) is Id and ind != 0:
                type_def.name = val._id
            elif val == "[":
                type_def.container = True
            elif type(val) is int:
                type_def.set_multi(val)

        if parser.debugDomm:
            print("DEBUG TypeDefAction returns: ", type_def)

        return type_def

class ConstraintSpecAction(SemanticAction):
    def first_pass(self, parser, node, children):
        temp_spec = ConstraintSpec()

        # We filter for strings to remove all `(` `)` `,` strings from children
        filter_children = (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction enter (children): ", children)

        for ind, val in enumerate(filter_children):
            if type(val) is Id and ind == 0:
                temp_spec.ident = val
            elif type(val) is Id and ind != 0:
                temp_spec.add_param(val)
            elif type(val) is StrObj :
                temp_spec.add_param(val.content)
            elif type(val) is int:
                temp_spec.add_param(val)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecAction returns: ", temp_spec)

        return temp_spec

class StrObj(object):
    """Helper class for string in StrObj"""
    def __init__(self, content = ""):
        super(StrObj, self).__init__()
        self.content = content

    def __repr__(self):
        return "StrObj[%s]" % self.content


class ConstraintParamAction(SemanticAction):
    """
    This action is used to get string content of a ConstraintSpec without
    getting comma or quotation marks.
    """
    def first_pass(self, parser, node, children):
        # Since this only appears when string is involved, we
        # just assume the second child is the strings content
        # Parse tree looks a bit like this:
        #   (") (string) (")
        string_param = ""
        for x in children:
            if x != '"':
                string_param = StrObj(x)

        if parser.debugDomm:
            print("DEBUG ConstraintParamAction returns: ", string_param)

        return string_param

class SpecsObj(object):
    """Helper class for ConstrainSpecsAction"""
    def __init__(self, specs = None):
        super(SpecsObj, self).__init__()
        self.specs = set()
        if specs:
            self.specs = specs

    def __repr__(self):
        return " SpecsObj(%s)" % self.specs

class ConstraintSpecListAction(SemanticAction):
    def first_pass(self, parser, node, children):
        list_specs = SpecsObj()

        filter_children = (x for x in children if type(x) is ConstraintSpec or type(x) is Id)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction enter (children): ", children)

        for val in filter_children:
            if type(val) is ConstraintSpec:
                list_specs.specs.add(val)
            elif type(val) is Id:
                temp = ConstraintSpec(ident = val)
                list_specs.specs.add(temp)

        if parser.debugDomm:
            print("DEBUG ConstraintSpecListAction returns (list_specs): ", list_specs)

        return list_specs

class RefObj(object):
    """Helper class for RefAction SemanticAction"""
    def __init__(self, ident):
        super(RefObj, self).__init__()
        self.ident = ident

    def __repr__(self):
        return " RefObj(%s)" % self.ident._id


class RefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        retVal = None

        for val in children:
            if type(val) is Id:
                retVal = RefObj(val)

        if parser.debugDomm:
            print("DEBUG RefAction returns: ", retVal)

        return retVal



class PropertyAction(SemanticAction):
    def first_pass(self, parser, node, children):
        prop = Property()

        if parser.debugDomm:
            print("DEBUG PropertyAction entered (children): {}\n".format(children))

        for val in children:
            if val == "unique":
                prop.unique = True

            elif val == "ordered":
                prop.ordered = True

            elif val == "readonly":
                prop.readonly = True

            elif val == "required":
                prop.required = True

            elif type(val) is TypeDef:
                prop.type_def = val

            elif val == "+":
                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj on enter: {}\n".format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n".format(prop.relationship))

                prop.relationship.containment = True
            elif type(val) is RefObj:
                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj on enter: {}\n".format(prop.relationship))

                if prop.relationship is None:
                    prop.relationship = Relationship()

                if parser.debugDomm:
                    print("DEBUG PropertyAction  RefObj (prop): {}\n".format(prop.relationship))

                prop.relationship.opposite_end = val.ident

                if parser.debugDomm:
                    print("DEBUG PropertyAction After RefObj (prop): {}\n".format(prop.relationship))
            elif type(val) is SpecsObj:
                for x in val.specs:
                    prop.add_constraint_spec(x)

            elif type(val) is NamedElement:
                if prop.type_def is None:
                    prop.type_def = TypeDef()

                prop.type_def.set_desc(val.short_desc, val.long_desc)

        if parser.debugDomm:
            print("DEBUG PropertyAction returns: ", prop)
            print("DEBUG PropertyAction returns prop.relationship", prop.relationship)

        return prop

class ExceptionAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered ExceptionAction")

        exception = ExceptionType()

        # We filter for strings to remove all `{` `}` and keywords strings from children
        filter_children =  (x for x in children if type(x) is not str)

        for val in filter_children:
            if type(val) is Id:
                exception.name = val._id
            elif type(val) is NamedElement:
                exception.set_desc(short_desc = val.short_desc, long_desc = val.long_desc)
            elif type(val) is Property:
                exception.add_prop(val)

        if parser.debugDomm:
            print("DEBUG  ExceptionAction returns ", exception)

        return exception

class ExtObj(object):
    """Helper object that carries a single reference"""
    def __init__(self, ref):
        super(ExtObj, self).__init__()
        self.ref = ref

    def __repr__(self):
        return " ExtObj (%s)" % self.ref

class ExtDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG ExtDefAction enter (children) ", children)
        # there are only two elements keyword and identifer
        for val in children:
            if type(val) is Id:
                retVal = ExtObj(ref = ClassifierBound(ref = val, type_of = ClassType.Entity))

                if parser.debugDomm:
                    print("DEBUG ExtDefAction returned ", retVal)

                return retVal

class DepObj(object):
    """Helper object that carries list of dependecies"""
    def __init__(self, rels):
        super(DepObj, self).__init__()
        assert type(rels) is list
        self.rels = rels

    def __repr__(self):
        retStr =  " DepObj ( "
        for val in self.rels:
            retStr += " %s " % val
        retStr += ")"
        return retStr

class DepDefAction(SemanticAction):
    def first_pass(self, parser, node, children):
        list_dependencies = []

        if parser.debugDomm:
            print("DEBUG Entered DepDefAction (children)", children)

        for val in children:
            if type(val) is Id:
                list_dependencies.append(ClassifierBound(ref = val))

        retVal = DepObj(rels = list_dependencies)

        if parser.debugDomm:
            print("DEBUG Entered DepDefAction returns ", retVal)

        return retVal

class OpParamAction(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debugDomm:
            print("DEBUG Entered OpParamAction (children)", children)

        param = OpParam()

        for val in children:
            if type(val) is TypeDef:
                param.type_def = val
            elif type(val) is NamedElement:
                param.set_from_named(val)
            elif type(val) is SpecsObj:
                for x in val:
                    param.constraints.add(x)
            elif val == "ordered":
                param.ordered = True
            elif val == "required":
                param.required = True
            elif val == "unique":
                param.unique = True

        if parser.debugDomm:
            print("DEBUG Entered OpParamAction returns ", param)

        return param
class OperationAction(SemanticAction):
    def first_pass(self, parser, node, children):
        filter_children = (x for x in children if x != "(" and x != ")" and x != "{" and x != "}")

        if parser.debugDomm:
            print("DEBUG Entered OperationAction (children)", children)

        oper = Operation()
        for val in filter_children:
            if parser.debugDomm:
                print("DEBUG OperationAction loop val: ", val)
            if type(val) is TypeDef:
                oper.type_def = val
            elif type(val) is NamedElement:
                oper.set_from_named(val)
            elif val == "ordered":
                oper.ordered = True
            elif val == "unique":
                oper.unique = True
            elif val == "required":
                oper.required = True
            elif type(val) is OpParam:
                oper.add_param(val)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    oper.add_constraint_spec(x)
            elif type(val) is Id:
                exc = ClassifierBound(ref = val, type_of = ClassType.ExceptType)
                oper.add_throws_exception(exc)

        if parser.debugDomm:
            print("DEBUG OperationAction returns", oper)
        return oper


class ServiceAction(SemanticAction):
    def first_pass(self, parser, node, children):

        # We filter for strings to remove all `{` `}` and keywords strings from children
        filter_children =  (x for x in children if type(x) is not str)

        if parser.debugDomm:
            print("DEBUG Entered ServiceAction (children)", children)

        service = Service()

        for val in filter_children:
            if type(val) is Id:
                service.name = val._id
            elif type(val) is NamedElement:
                service.set_desc(val.short_desc, val.long_desc)
            elif type(val) is ExtObj:
                if parser.debugDomm:
                    print("DEBUG Entered ServiceAction extends ", service)
                service.set_extends(val.ref)
            elif type(val) is DepObj:
                service.set_dependencies(val.rels)
            elif type(val) is SpecsObj:
                for x in val.specs:
                    service.add_constraint_spec(x)
            elif type(val) is Operation:
                service.add_operation(val)

        if parser.debugDomm:
            print("DEBUG Entered ServiceAction returns ", service)

        return service


