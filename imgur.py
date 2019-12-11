import base64
import json
import requests
from PIL import Image
from base64 import b64encode
import numpy
import mpld3

def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = numpy.fromstring ( fig.canvas.tostring_argb(), dtype=numpy.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll ( buf, 3, axis = 2 )
    return buf

imgurID = '44dc4e7f6a501c1'
imgurSecret = 'aa1c760cc685c9438cf5de53bc4e5e7cf800ba09'
 
def fig2img(fig):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data (fig)
    w, h, d = buf.shape
    return Image.fromstring( "RGBA", ( w ,h ), buf.tostring( ) )

def upload(plt, title):

	html_fig = mpld3.fig_to_html(plt)
	# print(html_fig)
	return html_fig
	# client_id = imgurID

	# headers = {"Authorization": "Client-ID " + imgurID}

	# api_key = 'aa1c760cc685c9438cf5de53bc4e5e7cf800ba09'

	# url = "https://api.imgur.com/3/upload.json"

	# j1 = requests.post(
	#     url, 
	#     headers = headers,
	#     data = {
	#         'key': api_key, 
	#         'image': b64encode(img.read()),
	#         'type': 'base64',
	#         'name': title + '.jpg',
	#         'title': 'Picture no. 1'
	#     }
	# )

