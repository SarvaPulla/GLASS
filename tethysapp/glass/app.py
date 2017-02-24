from tethys_sdk.base import TethysAppBase, url_map_maker


class Glass(TethysAppBase):
    """
    Tethys app class for Glass.
    """

    name = 'GLASS'
    index = 'glass:home'
    icon = 'glass/images/icon.gif'
    package = 'glass'
    root_url = 'glass'
    color = '#e74c3c'
    description = 'Glofas Prototype'
    tags = ''
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='glass',
                           controller='glass.controllers.home'),
                    UrlMap(name='details',
                           url='details',
                           controller='glass.controllers.details'),
                    UrlMap(name='details2',
                           url='details2',
                           controller='glass.controllers.details2'),
                    UrlMap(name='compare',
                           url='compare',
                           controller='glass.controllers.compare'),
                    UrlMap(name='soap-api',
                           url='glass/soap-api',
                           controller='glass.controllers.soap_api'),
                    UrlMap(name='soap-var',
                           url='glass/soap-var',
                           controller='glass.controllers.soap_var'),
        )

        return url_maps