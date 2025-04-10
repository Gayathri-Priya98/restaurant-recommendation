from sklearn.metrics import precision_score, recall_score

def evaluate_model(true_labels, predicted_labels):
    precision = precision_score(true_labels, predicted_labels, average='weighted')
    recall = recall_score(true_labels, predicted_labels, average='weighted')
    
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}")
    return precision, recall

if __name__ == "__main__":
    # Dummy Data
    true_labels = [1, 0, 1, 1, 0]
    predicted_labels = [1, 0, 1, 0, 0]
    
    evaluate_model(true_labels, predicted_labels)
