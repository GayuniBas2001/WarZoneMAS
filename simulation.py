from model import WarZoneModel

if __name__ == "__main__":
    # Parameters for the simulation
    width, height = 20, 20
    n_civilians = 50
    n_military = 10
    n_terrorists = 5

    # Create and run the model
    model = WarZoneModel(width, height, n_civilians, n_military, n_terrorists)
    for i in range(100):
        print(f"Step {i}")
        model.step()
