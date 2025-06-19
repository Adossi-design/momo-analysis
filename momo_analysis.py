from backend.api import create_app
from waitress import serve
import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(description='MTN MoMo Transaction Analysis System')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    app = create_app()
    
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if args.debug:
        logging.info("Running in debug mode")
        app.run(debug=True, host=args.host, port=args.port)
    else:
        logging.info(f"Starting production server on {args.host}:{args.port}")
        serve(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
