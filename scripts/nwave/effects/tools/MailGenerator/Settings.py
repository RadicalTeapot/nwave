# -*- coding: utf-8 -*-
"""DOCSTRING."""


class Settings:
    WINDOW_TITLE = 'Mail Generator'
    WIDTH = 1200
    HEIGHT = 1000

    RECIPIENTS = [
        'grp_sup_corgi@nwavedigital.com',
        'grp_lgtcomp_corgi@nwavedigital.com'
    ]

    # Path to internal mail server
    MAIL_SERVER = 'mail2.nwavedigital.local'
    # Subject line of the mail
    SUBJECT = '[{prod_name}][FX] {shot} {assets} are published'

    MAIL_TEMPLATE = "^.+?@nwavedigital.com$"

    VOLUME_SETTINGS = [
        "The render settings, to light this asset, are:",
        "Sampling / Volume Indirect : minimum at 2",
        "Ray Depth / Volume at 4"
    ]

    PLAIN_TEXT = """

    {assets} are published for shot {shot}

    <http://corgi.zefiro.nwavedigital.local/sequences/{sequence}/shots/{shot}>
    <http://corgi.zefiro.nwavedigital.local/sequences/{sequence}/shots/{shot}>

    {assets} have been published for shot {shot} and are ready for LGT.

    Shot link:
    {tasks}
    http://corgi.zefiro.nwavedigital.local/sequences/{sequence}/shots/{shot}

    Movies:
    {movies}

    Remarks:
    {remarks}

    Thank you !

    {user}

    This is an automatic notification message sent by the fx team on Corgi.
    """

    DEFAULT_HTML = """
    <body>
        <div style="position: absolute; left: 50%; top: 50%; transform: translateX(-50%) translateY(-50%); text-align: center;">
            <p>Click on 'Preview' to get a preview of the email.</p>
        </div>
    </body>
    """

    HTML_TEMPLATE = """
    <body>
        <div style="width: 100%; font-family: Ubuntu, Helvetica,sans-serif; text-rendering: optimizeLegibility; font-size: 14px;line-height: 1.42857; color: #333333; background-color:#ffffff;">
            <div style="padding: 10px;">
              {extra_data}
              <div style="width: 100%; max-width: 800px; margin-left: auto; margin-right: auto; border: 1px solid #dddddd; border-radius: 4px; box-shadow: 0px 1px 1px rgba(0, 0, 0, 0.05);">
                <div style="padding: 5px 15px 15px 15px;">
                  <div style="padding: 5px 15px 15px 15px;">
                    <div>
                      <div style="width: 100%;">
                        <h2 style="font-size: 30px; font-weight: 500; margin-top: 1px; margin-bottom: 5px;">{assets} are published for shot {shot}</h2>
                      </div>
                    </div>
                    <div style="border-bottom: 1px solid #eeeeee; margin-top: 2%;"><span style="display: none;"></span></div>
                    <br>
                    <p style="margin: 0 0 10px;">{assets} have been published for shot <b>{shot}</b> and are ready for LGT.</p>

                    <p><u>Tasks:</u></p>
                    <div style="margin: 5px 10px 20px; word-wrap: break-word;">
                        <p>{tasks}</p>
                        <a moz-do-not-send="true" href="http://corgi.zefiro.nwavedigital.local/sequences/{sequence}/shots/{shot}">http://corgi.zefiro.nwavedigital.local/sequences/{sequence}/shots/{shot}</a>
                    </div>

                    <p><u>Movies:</u></p>
                    <div style="margin: 5px 10px 20px; word-wrap: break-word;">
                        {movies}
                    </div>

                    <p><u>Remarks:</u></p>
                    <div style="margin: 10px 10px 30px 20px; word-wrap: break-word;">
                        {remarks}<br/>
                        {images}
                    </div>

                    Thank you !
                    <div style="margin: 0 10px; width:100%; text-align:right; color:#909090">
                        <i>{user}</i>
                    </div>
                    <div style="border-bottom: 1px solid #eeeeee;
                      margin-top: 2%;"><span style="display: none;"></span>
                    </div>
                    <p style="margin: 1em 0 0; font-size: 70%;">This is an automatic notification message sent by the fx team on Corgi.</p>
                  </div>
                </div>
              </div>
            </div>
        </div>
    </body>
    """

    MOVIE_TYPES = ['*.mov', '*.avi']
    MOVIE_TEMPLATE = '<a moz-do-not-send="true" href="zx:file:{href}">{path}</a><br/>'
    MOVIE_PLAIN_TEXT = '''
    {path}
    <zx:file:{href}>
    '''

    IMAGE_TYPES = ['*.jpg', '*.png']
    IMAGE_TEMPLATE = '<img moz-do-not-send="true" style="border-radius: 5px; width: 100%;" src="file:///{path}" alt="">'
    IMAGE_MAIL_TEMPLATE = '<img moz-do-not-send="true" style="border-radius: 5px; width: 100%;" src="cid:{image_name}" alt="">'
