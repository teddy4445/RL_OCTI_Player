import multiprocessing
import torch

from octigame import OctiGame
from octinet import OctiNet
from playerai import OctiAIPlayer
from rltrainer import RLTrainer


def self_play_worker(worker_id, rounds, model_path, return_dict):
    """Worker function for running self-play games in parallel."""
    model = OctiNet()
    model.load_state_dict(torch.load(model_path))  # Load shared model
    model.eval()

    trainer = RLTrainer(model)
    game_history = []

    for _ in range(rounds):
        game = OctiGame(OctiAIPlayer("AI1", model), OctiAIPlayer("AI2", model))

        while not game.winner:
            board_state = game.board.to_vector()
            move = game.players[game.current_player].choose_move(game)
            game.make_move(move)
            game_history.append((board_state, None))  # Store moves

        outcome = 1 if game.winner == "AI1" else -1
        for i in range(len(game_history)):
            game_history[i] = (game_history[i][0], outcome)

        return_dict[worker_id] = game_history  # Store training data


def run_parallel_training(num_workers=4, rounds_per_worker=500):
    """Runs self-play training in parallel using multiprocessing."""
    model = OctiNet()
    torch.save(model.state_dict(), "octi_ai.pth")  # Save initial model

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    for i in range(num_workers):
        p = multiprocessing.Process(
            target=self_play_worker, args=(i, rounds_per_worker, "octi_ai.pth", return_dict)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()  # Wait for all processes to finish

    # Combine results and train on collected data
    trainer = RLTrainer(model)
    all_game_data = sum(return_dict.values(), [])

    for board_state, outcome in all_game_data:
        trainer.train_step(board_state, outcome)

    torch.save(model.state_dict(), "octi_ai_trained.pth")  # Save trained model


