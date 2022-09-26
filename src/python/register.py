from grongier.pex import Utils

 ## Register Python code
Utils.register_component("adapter","RedditInboundAdapter","/irisdev/app/src/python/reddit/",1,"Python.RedditInboundAdapter")
Utils.register_component("bs","RedditService","/irisdev/app/src/python/reddit/",1,"Python.RedditService")
Utils.register_component("bp","FilterPostRoutingRule","/irisdev/app/src/python/reddit/",1,"Python.FilterPostRoutingRule")
Utils.register_component("bo","FileOperationWithIrisAdapter","/irisdev/app/src/python/reddit/",1,"Python.FileOperationWithIrisAdapter")
Utils.register_component("bo","FileOperation","/irisdev/app/src/python/reddit/",1,"Python.FileOperation")
 