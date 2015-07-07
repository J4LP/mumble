import os
import yaml
import Ice
from mumble.app import create_app

with open('./config.yml') as f:
    config_file = yaml.load(f.read())

Ice.loadSlice('', ['-I' + Ice.getSliceDir(), config_file['SLICE_FILE']])

app = create_app(config_object=config_file)

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(os.environ.get('PORT', 5002)), debug=True)
