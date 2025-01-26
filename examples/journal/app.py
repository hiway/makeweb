"""
Journal App
"""

from quart import Quart, render_template
from datetime import datetime

app = Quart(__name__)

@app.route('/')
async def index():
    today = datetime.now().strftime('%B %d, %Y')
    return await render_template('index.html', today=today)

@app.route('/search')
async def search():
    # Will implement search functionality later
    return {'results': []}

if __name__ == '__main__':
    app.run(debug=True)
