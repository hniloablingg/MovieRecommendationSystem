from load_data import load_ratings
from collaborative_filtering import CollaborativeFilteringModel

def main():
    ratings = load_ratings()
    model = CollaborativeFilteringModel()
    model.train(ratings)

    # Save model
    model.save("./cf_model.pkl")

if __name__ == '__main__':
    main()
