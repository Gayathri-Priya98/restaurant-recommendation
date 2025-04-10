import torch
import torch.nn as nn
import torch.optim as optim
import torch_geometric.nn as pyg_nn
from torch_geometric.data import Data
from recomm_system.load_data import load_datasets
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# ✅ GCN Model
class GNNRecommender(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=16, output_dim=1):
        super(GNNRecommender, self).__init__()
        self.conv1 = pyg_nn.GCNConv(input_dim, hidden_dim)
        self.conv2 = pyg_nn.GCNConv(hidden_dim, output_dim)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

# ✅ Create Graph Data
def create_graph(business_df, review_df, user_df):
    user_df = user_df.drop_duplicates(subset=['user_id'])
    business_df = business_df.drop_duplicates(subset=['business_id'])

    user_df.loc[:, 'average_stars'] = user_df['average_stars'].fillna(0)
    business_df['stars'] = business_df['stars'].fillna(0)

    user_ids = {user: idx for idx, user in enumerate(user_df['user_id'].unique())}
    rest_ids = {rest: idx + len(user_ids) for idx, rest in enumerate(business_df['business_id'].unique())}

    edges = []
    ratings = []  # ✅ Store ratings for supervised learning

    for _, row in review_df.iterrows():
        user_idx = user_ids.get(row['user_id'])
        rest_idx = rest_ids.get(row['business_id'])
        if user_idx is not None and rest_idx is not None:
            edges.append([user_idx, rest_idx])
            ratings.append(row['review_stars'])  # ✅ Use review stars as labels

    edges += [[rest_idx, user_idx] for user_idx, rest_idx in edges]
    edge_index = torch.tensor(edges, dtype=torch.long).T

    user_features = torch.tensor(user_df.set_index('user_id')['average_stars'].reindex(user_ids.keys()).fillna(0).values, dtype=torch.float).view(-1, 1)
    rest_features = torch.tensor(business_df.set_index('business_id')['stars'].reindex(rest_ids.keys()).fillna(0).values, dtype=torch.float).view(-1, 1)

    x = torch.cat((user_features, rest_features), dim=0)
    
    y = torch.tensor(ratings, dtype=torch.float)
    if y.shape[0] != edge_index.shape[1] // 2:
        print(f"⚠️ Warning: y shape {y.shape} mismatched with edges {edge_index.shape}")

    return Data(x=x, edge_index=edge_index, y=y)

# ✅ Main Execution
if __name__ == "__main__":
    business_df, review_df, user_df = load_datasets()
    graph_data = create_graph(business_df, review_df, user_df)

    edge_index = graph_data.edge_index
    input_dim = graph_data.x.shape[1] if graph_data.x.dim() > 1 else 1
    model = GNNRecommender(input_dim, 16, 16)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    # ✅ Training
    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        output = model(graph_data.x, edge_index)

        # ✅ Ensure output size matches y_true
        y_true = graph_data.y.view(-1, 1)
        y_pred = output[:y_true.shape[0]]

        loss = loss_fn(y_pred, y_true)
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")

    print("✅ Training Completed!")
    torch.save(model.state_dict(), "gnn_recommender.pth")
    print("✅ Model Saved!")

    # ✅ Evaluation
    y_true = y_true.view(-1).detach().cpu().numpy()
    y_pred = y_pred.view(-1).detach().cpu().numpy()

# Trim `y_pred` if it's too long
    y_pred = y_pred[:len(y_true)]

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)

    print(f"📊 RMSE: {rmse:.4f}, MAE: {mae:.4f}")


