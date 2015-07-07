from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
import yaml
import Ice
from mumble.app import create_app

with open('./config.yml') as f:
    config_file = yaml.load(f.read())

Ice.loadSlice('', ['-I' + Ice.getSliceDir(), config_file['SLICE_FILE']])
app = create_app(config_object=config_file)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
