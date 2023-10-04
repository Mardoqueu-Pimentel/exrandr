from prettyprinter.prettyprinter import pretty_call_alt, register_pretty


def is_instance_of_attrs_class(value):
    cls = type(value)

    try:
        cls.__attrs_attrs__
    except AttributeError:
        return False

    return True


def pretty_attrs(value, ctx):
    cls = type(value)
    attributes = cls.__attrs_attrs__

    kwargs = []
    for attribute in attributes:
        if not attribute.repr:
            continue

        kwargs.append((attribute.name, getattr(value, attribute.name)))

    return pretty_call_alt(ctx, cls, kwargs=kwargs)


def install():
    register_pretty(predicate=is_instance_of_attrs_class)(pretty_attrs)
