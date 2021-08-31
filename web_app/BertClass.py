import torch.nn as nn
class BertClassifier(nn.Module):
    """
    Bert Model

    """

    def __init__(self, freeze_bert=False):

        super(BertClassifier, self).__init__()
        D_in, H, D_out = 768, 50, 2
        #BERT base model
        self.bert = BertModel.from_pretrained('bert-base-uncased')

        #Another layer
        self.classifier = nn.Sequential(
            nn.Linear(D_in, H),
            nn.ReLU(),
            # nn.Dropout(0.5), #comment when evaluation
            nn.Linear(H, D_out)
        )

        # Freeze the BERT model
        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False

    def forward(self, input_ids, attention_mask):
        """
        The forward process
        """
        outputs = self.bert(input_ids=input_ids,
                            attention_mask=attention_mask)

        # Only the [CLS] token will be taken as the output
        last_hidden_state_cls = outputs[0][:, 0, :]

        logits = self.classifier(last_hidden_state_cls)

        return logits
