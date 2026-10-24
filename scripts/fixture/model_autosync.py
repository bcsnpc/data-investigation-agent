"""Publisher-only plans for reversible Direct Lake automatic framing controls.

This follows Microsoft's semantic-link-labs directlake.set_autosync route.
No credential, network executor or investigation capability is installed here.
"""
import re
from urllib.parse import urlsplit
from uuid import UUID


class ModelAutoSyncScenario:
    def __init__(self,workspace,models,capabilities):
        self.workspace=str(UUID(workspace))
        if not isinstance(models,list)or not 1<=len(models)<=3:
            raise ValueError('AUTOSYNC_APPROVED_MODEL_BOUND')
        self.models={str(UUID(x))for x in models}
        if len(self.models)!=len(models):raise ValueError('AUTOSYNC_DUPLICATE_MODEL')
        if capabilities.get('status_code')!=200:raise ValueError('AUTOSYNC_NATIVE_CAPABILITIES_REQUIRED')
        context=capabilities.get('text',{}).get('@odata.context','')
        uri=urlsplit(context)
        if (uri.scheme!='https'or uri.username or uri.password or uri.port
                or not(uri.hostname=='api.powerbi.com'or re.fullmatch(r'[a-z0-9-]+\.analysis\.windows\.net',uri.hostname or''))
                or uri.path!='/v1.0/myorg/$metadata'or uri.query or uri.fragment!='capacities'):
            raise ValueError('AUTOSYNC_NATIVE_API_ROOT_REFUSED')
        self.root='https://'+uri.hostname

    def model_read(self,model):
        model=str(UUID(model))
        if model not in self.models:raise ValueError('AUTOSYNC_MODEL_OUTSIDE_APPROVED_SET')
        return {'method':'GET','url':self.root+'/metadata/models/'+model,'body':None}

    def settings_read(self,model,metadata):
        expected=self.model_read(model)
        if metadata.get('request')!=expected or metadata.get('status_code')!=200:
            raise ValueError('AUTOSYNC_MODEL_METADATA_BINDING_REQUIRED')
        native=metadata.get('text',{}).get('model',{})
        identity=native.get('id')
        if type(identity)is not int or not 1<=identity<=9223372036854775807:
            raise ValueError('AUTOSYNC_NATIVE_MODEL_ID_REQUIRED')
        return {'method':'GET','url':self.root+'/metadata/models/'+str(identity)+'/settings','body':None}

    def change(self,model,metadata,settings,*,expected,enabled):
        request=self.settings_read(model,metadata)
        if type(expected)is not bool or type(enabled)is not bool:
            raise ValueError('AUTOSYNC_BOOLEAN_REQUIRED')
        if (settings.get('request')!=request or settings.get('status_code')!=200
                or settings.get('text',{}).get('directLakeAutoSync')is not expected):
            raise ValueError('AUTOSYNC_SETTING_PREIMAGE_CHANGED')
        if expected==enabled:return {'status':'ALREADY_AT_REQUESTED_SETTING','mutations':0}
        return {'method':'POST','url':request['url'],'body':{'directLakeAutoSync':enabled},
                'expected_status_code':204}
