from nltk.featstruct import FeatureValueSet
from numpy import format_float_scientific
import pandas as pd
from tqdm import tqdm
from resources.transformer_augmenter import transformer_augmenter
from nltk.tokenize.toktok import ToktokTokenizer
from config import config
from sklearn.model_selection import train_test_split


def augment_data(df, verbose=False):

    train_corpus, test_corpus, train_label_names, test_label_names = train_test_split(
        df["text"], df["category"], test_size=0.33, random_state=42
    )

    tokenizer = ToktokTokenizer()
    augmenter = transformer_augmenter()

    _, train_corpus_to_augment = train_test_split(
        train_corpus, test_size=config.percent_to_augment, random_state=42
    )
    n_sentences = len(train_corpus_to_augment)

    augmented_sentences = []
    aug_sent_categories = []

    tokenized_text = [tokenizer.tokenize(text) for text in train_corpus_to_augment]
    for i in tqdm(range(n_sentences)):
        sentence = tokenized_text[i]
        category = train_label_names.iloc[i]

        augmented_sentences.extend(
            augmenter.generate(
                sentence,
                new_sent_per_sent=config.new_sent_per_sent,
                num_words_replace=config.num_words_replace,
                list_of_words=False,
                verbose=verbose,
            )
        )

        for _ in range(config.new_sent_per_sent + 1):
            aug_sent_categories.append(category)

    print("number of the original sentences: {}".format(n_sentences))
    print("number of the augmented sentences: {}".format(len(augmented_sentences)))

    aug_train_df = pd.DataFrame(
        list(zip(augmented_sentences, aug_sent_categories)),
        columns=["text", "category"],
    )

    train_df = pd.DataFrame(
        list(zip(train_corpus, train_label_names)),
        columns=["text", "category"],
    )

    test_df = pd.DataFrame(
        list(zip(test_corpus, test_label_names)),
        columns=["text", "category"],
    )

    aug_train_df.to_csv(config.aug_file_path, index=False)
    train_df.to_csv(config.train_file_path, index=False)
    test_df.to_csv(config.test_file_path, index=False)
    return aug_train_df, test_df


