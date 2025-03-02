from octigame import OctiGame
from octigamegui import OctiGameGUI
from octinet import OctiNet
from player import Player
from rltrainer import RLTrainer


class Main:

    def __init__(self):
        self.trainer = RLTrainer(OctiNet())

    def run(self):
        print("Welcome to Octi AI!")
        print("1: Train AI")
        print("2: Play against AI")
        print("3: Play Human vs Human")
        choice = str(3) # input("Select an option (1-3): ").strip()

        if choice == "1":
            self.train_ai()
        elif choice == "2":
            self.play_vs_ai()
        elif choice == "3":
            self.play_human_vs_human()
        else:
            print("Invalid choice. Exiting...")

    def train_ai(self):
        epochs = int(input("Enter number of training epochs: ").strip())
        print(f"Training AI for {epochs} epochs...")
        self.trainer.train(epochs=epochs)
        print("Training complete!")

    def play_vs_ai(self):
        print("Starting Human vs AI game...")
        self.trainer.play_vs_human()

    def play_human_vs_human(self):
        print("Starting Human vs Human game...")
        OctiGameGUI(OctiGame(Player(0), Player(1))).run()


if __name__ == "__main__":
    main = Main()
    main.run()
