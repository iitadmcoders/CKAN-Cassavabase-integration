import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CkanbasePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer   
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ckanbase')
        toolkit.add_resource('temp', 'temp_files')

    def before_map(self, map):
    	map.connect('cassbase','/cassbase', controller='ckanext.ckanbase.controller:CkanbaseController', action='cbase')
    	map.connect('/cassavabase_data', controller='ckanext.ckanbase.controller:CkanbaseController', action='cassava_data')
    	return map