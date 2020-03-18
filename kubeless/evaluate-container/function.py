import sys
from os import path
sys.path.append( '/kubeless' )
import container

def test(event, context):
    # In Kubeless you're not a root user, so you can only write to folders regarding the permissions
    # A folder that is owned by the function user is /kubeless
    return container.evaluate("/kubeless", "text.txt", "Test")
