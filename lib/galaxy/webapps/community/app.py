import sys, config
import galaxy.webapps.community.model
from galaxy.web import security
from galaxy.tags.tag_handler import CommunityTagHandler

class UniverseApplication( object ):
    """Encapsulates the state of a Universe application"""
    def __init__( self, **kwargs ):
        print >> sys.stderr, "python path is: " + ", ".join( sys.path )
        # Read config file and check for errors
        self.config = config.Configuration( **kwargs )
        self.config.check()
        config.configure_logging( self.config )
        if self.config.enable_next_gen_tool_shed:
            # We don't need a datatypes_registry since we have no datatypes
            pass
        else:
            import galaxy.webapps.community.datatypes
            # Set up datatypes registry
            self.datatypes_registry = galaxy.webapps.community.datatypes.Registry( self.config.root, self.config.datatypes_config )
            galaxy.model.set_datatypes_registry( self.datatypes_registry )
        # Determine the database url
        if self.config.database_connection:
            db_url = self.config.database_connection
        else:
            db_url = "sqlite://%s?isolation_level=IMMEDIATE" % self.config.database
        # Initialize database / check for appropriate schema version
        from galaxy.webapps.community.model.migrate.check import create_or_verify_database
        create_or_verify_database( db_url, self.config.database_engine_options )
        # Setup the database engine and ORM
        from galaxy.webapps.community.model import mapping
        self.model = mapping.init( self.config.enable_next_gen_tool_shed,
                                   self.config.file_path,
                                   db_url,
                                   self.config.database_engine_options )
        # Security helper
        self.security = security.SecurityHelper( id_secret=self.config.id_secret )
        # Tag handler
        self.tag_handler = CommunityTagHandler()
        # Load security policy
        self.security_agent = self.model.security_agent
    def shutdown( self ):
        pass
