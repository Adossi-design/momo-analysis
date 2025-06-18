from backend.api import app
from waitress import serve
import logging
import argparse

logging.basicConfig(level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(description='MTN MoMo Transaction Analysis System')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if args.debug:
        logging.info("Running in debug mode")
        app.run(debug=True, host=args.host, port=args.port)
    else:
        logging.info(f"Starting production server on {args.host}:{args.port}")
        serve(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
