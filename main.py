import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from router import analyze_and_route

# Initialize colors
init(autoreset=True)
load_dotenv()

def print_header():
    print(Fore.CYAN + Style.BRIGHT + "="*50)
    print(Fore.CYAN + Style.BRIGHT + " "*15 + "AI ROUTER SYSTEM")
    print(Fore.CYAN + Style.BRIGHT + "="*50)
    print(Fore.YELLOW + "Main AI: " + Fore.WHITE + "Local Ollama (Qwen)")
    print(Fore.YELLOW + "Workers: " + Fore.WHITE + "Cloud APIs (OpenRouter)")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print(Fore.RED + "\nWARNING: OPENROUTER_API_KEY is not set in .env file.")
        print(Fore.RED + "Cloud workers will not function until this is provided.")
    print(Fore.CYAN + Style.BRIGHT + "="*50 + "\n")

def main():
    print_header()
    print("Type 'exit' or 'quit' to close the application.\n")
    
    while True:
        try:
            user_input = input(Fore.GREEN + "User > " + Fore.WHITE)
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            # Route and execute
            result = analyze_and_route(user_input)
            
            # Print final result
            print(Fore.MAGENTA + "\n[System Status] ")
            print(Fore.WHITE + result)
            print("-"*50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(Fore.RED + f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
