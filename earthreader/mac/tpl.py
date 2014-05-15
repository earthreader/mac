""":mod:`earthreader.mac.tpl` --- HTML templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader

__all__ = 'env', 'loader', 'render_template'

loader = PackageLoader('earthreader.mac')
env = Environment(loader=loader, autoescape=True)


def render_template(name, **values):
    template = env.get_template(name)
    return template.render(values)