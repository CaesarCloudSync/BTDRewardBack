docker run  -p 6379:6379 -d redis redis-server --save 60 1 --loglevel warning
python main.py