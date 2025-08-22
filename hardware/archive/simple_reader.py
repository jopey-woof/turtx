import sys

def main():
    """
    Reads from standard input and prints each line.
    This is designed to capture the 'typed' output from the TemperhUM sensor.
    """
    print("Ready to capture sensor output. Please press the button on the sensor.")
    print("Press Ctrl+C to exit.")
    
    try:
        for line in sys.stdin:
            print(f"Received: {line.strip()}")
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()