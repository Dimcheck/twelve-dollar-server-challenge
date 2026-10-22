from starlette.responses import JSONResponse


# root
async def homepage(request):
    return JSONResponse({'data': 'welcome'})


# health check
async def get_health(request):
    ...


# get latest 20 posts
async def get_posts(request):
    ...


# get post by id
async def get_post(request):
    ...


# create a post (auth)
async def create_post(request):
    ...


# like a post (auth)
async def create_like(request):
    ...