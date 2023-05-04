# -*- coding: utf-8 -*-
"""hw_recogs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1flnjCG_BY4eEua4m2GrX0QG9bRQ7ePm4

# Homework and bakeoff: Compositional generalization
"""

__author__ = "Christopher Potts and Zhengxuan Wu"
__version__ = "CS224u, Stanford, Spring 2023"

"""[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cgpotts/cs224u/blob/master/hw_recogs.ipynb)
[![Open in SageMaker Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/cgpotts/cs224u/blob/master/hw_recogs.ipynb)

If Colab is opened with this badge, please save a copy to drive (from the File menu) before running the notebook.

## Overview

This assignment is about _compositional generalization_. We are going to assess the degree to which our apparently very good models have learned to process and interpret language _systematically_. To do this, we are going to ask them to interpret novel combinations of familiar words and phrases. For humans, these tasks are very easy. For our models, the situation seems to be quite different.

The basis for the assignment is the ReCOGS dataset of [Wu, Manning, and Potts 2023](https://arxiv.org/abs/2303.13716). ReCOGS modifies the COGS dataset of [Kim and Linzen 2020](https://aclanthology.org/2020.emnlp-main.731) in a number of ways, with the goal of more directly assessing the interpretive abilities of models.

The assignment questions are fairly diverse. Question 1 asks you to conduct a specific analysis of the ReCOGS dataset, and Question 2 follows this up with a corresponding analysis of the errors made by a top-performing ReCOGS model. For Question 3, you try some in-context learning with DSP. And then we open things up as usual: you can do anything you want for your original system, and you enter that system's predictions into a bakeoff.

There is only one rule that we need to enforce throughout this work:

__You cannot train your system on any examples from `dataset["gen"]`, nor can the output representations from those examples be included in any prompts used for in-context learning.__

The nature of your original system is otherwise unconstrained.

## Set-up
"""

try:
    # This library is our indicator that the required installs
    # need to be done.
    import datasets
except ModuleNotFoundError:
    !git clone https://github.com/cgpotts/cs224u/
    !pip install -r cs224u/requirements.txt
    import sys
    sys.path.append("cs224u")

import os
import pandas as pd
from compgen import check_set_equal_neoD as recogs_exact_match

"""The default location of the data:"""

SRC_DIRNAME = os.path.join("data", "recogs")

"""The following code should grab the dataset for you; if it fails for any reason, you can manually download it from [this link](https://web.stanford.edu/class/cs224u/data/recogs.tgz) and then put it in `SRC_DIRNAME`."""

if not os.path.exists(SRC_DIRNAME):
    !mkdir -p data
    !wget https://web.stanford.edu/class/cs224u/data/recogs.tgz -P data
    !tar xvf data/recogs.tgz -C data/

"""## Load the COGS and ReCOGS datasets"""

def load_split(filename):
    return pd.read_csv(
        filename,
        delimiter="\t",
        names=['input', 'output', 'category'])

dataset = {}

for splitname in ("train", "dev", "gen"):
    dataset[splitname] = load_split(f"{SRC_DIRNAME}/{splitname}.tsv")

"""Here's a look at the dataset. Fundamentally, the task is to map simple English sentences to logical forms. For ReCOGS, you need only predict these forms up to semantic equivalence, which means that we abstract away from the order of the conjuncts and the names of specific variables."""

dataset['train'].head(2)

"""The `dataset['gen']` section is divided up into different 21 categories. A category name `X_to_Y` or `only_seen_as_X_as_Y`  means that specific phrases were seen only as `X` in training and will encounter those phrases as `Y` at test time."""

sorted(dataset['gen'].category.unique())

"""## Question 1: Proper names and their semantic roles

A number of the COGS/ReCOGS generalization categories assess models on their ability to handle proper names appearing in novel positions at test time. For example, in the `obj_to_subj_proper` category, models encounter proper names that appeared in the train set only in grammatical object position (e.g., _see Sandy_), and then they are asked to make predictions about cases where those names are grammatical subjects (_Sandy left_). These changes have systematic effects on the grammatical roles that the meanings of these names play semantically. In particular, subjects are likely to play `agent` roles and objects are likely to play `theme` roles.

### Task 1: Pattern-based analysis function [1 point]

Write a function that scans ReCOGS logical forms to determine what role proper names play. The following are the core steps:

1. Identify proper names. All and only proper names begin with capital letters in these LFs, and proper names consist only of ascii letters. The format is, informally, `Name ( d+ )`, as in `Sandy ( 47 )`.

2. Identify role expressions. The pattern is always `role ( d+ , d+ )`, as in `agent ( 1 , 47 )`. Here, the first variable is for the associated event, and the second is the role argument. The possible roles are `agent`, `theme`, and `recipient`.

3. Determine which of the above are linked in the sense that the variable names are the same. A given name can link to multiple role expressions (or none at all), and LFs can contain multiple names and multiple role expressions.

To do the above, you just need to complete the function `get_propername_role`. The test should clear up any ambiguity and help you iterate to a solution.
"""

import re

def get_propername_role(s):
    """Extract from `s` all the pairs `(name, role)` determined by
    binding relationships. There can be multiple tokens of the same
    name with different variables, as in "Kim ( 1 )" and "Kim ( 47 )",
    and there can be instances in which a single name with variable
    like "Kim ( 1 )" binds into multiple role expressions like
    "agent ( 4 , 1 )" and "theme ( 6 , 1 )". Your function should
    cover all these cases.

    We've suggested a particular program design to get you started,
    but you are free to do something different and perhaps cleverer
    if you wish!

    Parameters
    ----------
    s: str

    Returns
    -------
    set of tuples `(name, role)` where `name` and `role` are str
    """
    # Step 1: Define a regex for "name ( var )" expressions:
    ##### YOUR CODE HERE
    name_pattern = r'[A-Z][a-z]* \( \d+ \)'


    # Step 2: Define a regex for "role ( var , var )" expressions:
    ##### YOUR CODE HERE
    # role_pattern = r'(agent|theme|recipient) \(\s*\d+\s*,\s*\d+\s*\)'
    role_pattern = r'(?:agent|theme|recipient) \(\s*\d+\s*,\s*\d+\s*\)'


    # Step 3: Use `findall` with both of your regexs:
    ##### YOUR CODE HERE
    name_matches = re.findall(name_pattern, s)
    role_matches = re.findall(role_pattern, s)


    # Step 4: Loop overall combinations of matches from your regexs
    # to build `data` as a set of pairs `(name, role)`:
    data = set()
    ##### YOUR CODE HERE
    for name_match in name_matches:
        name = re.match(r'[A-Z][a-z]*', name_match).group(0)
        name_var = re.findall(r'\d+', name_match)[0]
        for role_match in role_matches:
            role = re.match(r'(agent|theme|recipient)', role_match).group(0)
            role_var = re.findall(r'\d+', role_match)
            if name_var in role_var:
                data.add((name, role))

    # Step 5: Return `data`:
    ##### YOUR CODE HERE
    return data

def test_get_propername_role(func):
    examples = [
        # Standard case:
        (
            "Bella ( 7 ) ; smile ( 4 ) AND agent ( 4 , 7 )", 
            {("Bella", "agent")}
        ),
        # No binding:
        (
            "Riley ( 37 ) ; theme ( 4 , 7 )", 
            set()
        ),
        # Two tokens of the same name referring to different entities:
        (
            "Riley ( 37 ) ; Riley ( 4 ) ; theme ( 1 , 37 ) AND agent ( 1 , 4 )",
            {("Riley", "theme"), ("Riley", "agent")},
        ),
        # Two names:
        (
            "Riley ( 4 ) ; Emma ( 243 ) ; recipient ( 6 , 4 ) AND agent ( 6, 243 )",
            {("Riley", "recipient"), ("Emma", "agent")},
        ),
        # One name binding into multiple role expressions:
        (
            "Riley ( 4 ) ; agent ( 6 , 4 ) AND theme ( 6, 4 )",
            {("Riley", "theme"), ("Riley", "agent")},
        ),
        # Nothing to match:
        (
            "no proper names",
            set()
        )
    ]
    errcount = 0
    for ex, expected in examples:
        result = func(ex)
        if expected != result:
            errcount += 1
            print(f"Error for `{func.__name__}`:"
                  f"\n\tInput: {ex}"
                  f"\n\tExpected: {expected}"
                  f"\n\tGot: {result}")
    if errcount == 0:
        print(f"No errors detected for `{func.__name__}`")

test_get_propername_role(get_propername_role)

"""### Task 2: Finding challenging names [1 point]

You can now use your code to find the names that will be the most challenging because their train/gen roles are disjoint. To do this, you just need to complete the function `find_name_roles`:
"""

from collections import defaultdict

def find_name_roles(split_df, colname="output"):
    """Create a map from names to dicts mapping roles to counts: the
    number of time the name appears with role in `split_df`:

    Parameters
    ----------
    split_df : pd.DataFrame
        Needs to have a column called `colname`.
    colname: str
        Column to target with `get_propername_role`. Default: "output".

    Returns
    -------
    `defaultdict` mapping names to roles to counts
    """
    # This is a convenient way to create a multidimensional count dict:
    # You can access it out of the box as `all_roles[key1][key2] += 1`.
    all_roles = defaultdict(lambda : defaultdict(int))
    
    # Apply `get_propername_role` to every value in the target column
    # and aggregate the results into `all_roles`:
    ##### YOUR CODE HERE
    for s in split_df[colname]:
        propername_role_tuples = get_propername_role(s)
        for name, role in propername_role_tuples:
            all_roles[name][role] += 1


    # Return `all_roles`:
    return all_roles

"""A quick test:"""

def test_find_name_roles(func):
    df = pd.DataFrame({
        "tester": [
            "Bella ( 7 ) ; agent ( 4 , 7 )",
            "Bella ( 7 ) ; agent ( 4 , 7 )",
            "Riley ( 37 ) ; agent ( 4 , 37 )",
            "Riley ( 3 ) ; theme ( 4 , 3 )",
            "Emma ( 37 ) ; theme ( 4 , 7 )"
        ]})
    expected = {
        "Bella": {"agent": 2},
        "Riley": {"agent": 1, "theme": 1}
    }
    result = func(df, colname="tester")
    if result != expected:
        print(f"Error for `{func.__name__}`:"
              f"\n\tExpected:{expected}"
              f"\n\tGot: {result}")
    else:
        print(f"No errors found for `{func.__name__}`")

test_find_name_roles(find_name_roles)

"""Once the test passes, this analysis should be informative:"""

train_roles = find_name_roles(dataset['train'])

sorted(train_roles.items(), key=lambda x: len(x[1]))[: 3]

gen_roles = find_name_roles(dataset["gen"])

sorted(gen_roles.items(), key=lambda x: len(x[1]))[: 3]

"""We will return to these troublemakers in a bit.

## Pretrained ReCOGS models

We launch now into an extended interlude before Question 2. For Question 2, you will work with a ReCOGS model that we trained for you. This interlude presents the code needed to work with this model. We are exposing these details to you in case you want to use this code to train or fine-tune your own models for your original system.

### Tokenization

Here is a function for creating Hugging Face `PreTrainedTokenizerFast` tokenizers based on a provided vocab file. It pretty much just splits on whitespace and adds special tokens. Chris originally planned to have writing this be a homework question, but it turned out to be very difficult and confusing for him to write, so he decided to just present it to you in the hope that it helps you with similar tasks in the future.
"""

from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import WhitespaceSplit
from tokenizers.processors import TemplateProcessing
from transformers import PreTrainedTokenizerFast


def get_tokenizer(vocab_filename):
    with open(vocab_filename) as f:
        vocab = f.read().splitlines()
    vocab_size = len(vocab)
    vocab = dict(zip(vocab, list(range(vocab_size))))
    tok = Tokenizer(WordLevel(vocab, unk_token='[UNK]'))
    # This definitely needs to be done here and in the construction of
    # `PreTrainedTokenizerFast`. Don't be tempted to "clean this up"!
    tok.add_special_tokens(["[BOS]", "[UNK]", "[PAD]", "[EOS]"])
    tok.pre_tokenizer = WhitespaceSplit()
    tok.post_processor = TemplateProcessing(
        single=f"[BOS]:0 $A:0 [EOS]:0",
        special_tokens=[
            ("[BOS]", tok.token_to_id("[BOS]")),
            ("[EOS]", tok.token_to_id("[EOS]"))])
    return PreTrainedTokenizerFast(
        tokenizer_object=tok,
        bos_token="[BOS]",
        unk_token="[UNK]",
        pad_token="[PAD]",
        eos_token="[EOS]",
        # This vital; otherwise any periods will have their leading
        # spaces removed, which is wrong for COGS/ReCOGS.
        clean_up_tokenization_spaces=False)

"""We will have separate tokens for the encoder and the decoder:"""

enc_tokenizer = get_tokenizer(os.path.join(SRC_DIRNAME, "src_vocab.txt"))

enc_tokenizer.tokenize(
    "A sailor was helped", 
    add_special_tokens=True)

dec_tokenizer = get_tokenizer(os.path.join(SRC_DIRNAME, "tgt_vocab.txt"))

dec_tokenizer.tokenize(
    "sailor ( 53 ) ; help ( 7 ) AND theme ( 7 , 53 )", 
    add_special_tokens=True)

"""### Dataset

Next is a dataset utility. Chris was originally going to have you write this yourselves, since it is useful to know how to write these utilities, and the task is really just to use our tokenizers appropriately. However, since `collate_fn` has to be a static method with fixed arguments, we can't easily pass in these tokenizers to it! As a result, we have to do all the tokenization at once ahead of time and then redo all the masking work for each batch. So Chris did this for you in the hope that this will be useful to you in the future.
"""

import torch

class RecogsDataset(torch.utils.data.Dataset):
    def __init__(self, enc_tokenizer, dec_tokenizer, X, y=None):
        self.X = [enc_tokenizer.encode(s) for s in X]
        self.y = y
        if y is not None:
            self.y = [dec_tokenizer.encode(s) for s in y]

    @staticmethod
    def collate_fn(batch):
        """Unfortunately, we can't pass the tokenizer in as an argument
        to this method, since it is a static method, so we need to do
        the work of creating the necessary attention masks."""
        def get_pad_and_mask(vals):
            lens = [len(i) for i in vals]
            maxlen = max(lens)
            pad = []
            mask = []
            for ex, length in zip(vals, lens):
                diff = maxlen - length
                pad.append(ex + ([0] * diff))
                mask.append(([1] * length) + ([0] * diff))
            return torch.tensor(pad), torch.tensor(mask)
        batch_elements = list(zip(*batch))
        X = batch_elements[0]
        X_pad, X_mask = get_pad_and_mask(X)
        if len(batch_elements) == 1:
            return X_pad, X_mask
        else:
            y = batch_elements[1]
            y_pad, y_mask = get_pad_and_mask(y)
            # Repeat `y_pad` because our optimizer expects to find
            # labels in final position. These will not be used because
            # Hugging Face will calculate the loss for us.
            return X_pad, X_mask, y_pad, y_mask, y_pad

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is None:
            return (self.X[idx],)
        else:
            return (self.X[idx], self.y[idx])

"""The following just illustrate how to work with the above utility:"""

ex_dataset = RecogsDataset(
    enc_tokenizer,
    dec_tokenizer,
    dataset['train'].input.head(20),
    y=dataset['train'].output.head(20))

ex_dataloader = torch.utils.data.DataLoader(
    ex_dataset,
    batch_size=2,
    shuffle=True,
    pin_memory=True,
    collate_fn=ex_dataset.collate_fn)

ex_batch = iter(ex_dataloader)

"""This will show you batches. Since `batch_size=2` for `dataloader`, this will be a tuple where each element has two lists. The structure is determined by `collate_fn` in `RecogsDataset`: 

`X_pad, X_mask, y_pad, y_mask, y_pad`

where `y_pad` is repeated in the final position to meet the interface specifications of `torch_base_model.py`, in case you decide to train models yourself. (See details below; Hugging Face calculates the loss itself, which is ultimately nice but a bit non-standard.)
"""

next(ex_batch)

"""### Model basics

Now we come to the model itself. We will first load it and explore it a bit, and then we will define a nice classifier interface for it.
"""

from transformers import EncoderDecoderModel

encdec = EncoderDecoderModel.from_pretrained(f"ReCOGS/ReCOGS-model")

"""A single illustrative example:"""

ex_inputs = enc_tokenizer.batch_encode_plus(
    ["A rose was helped by a dog ."], 
    return_tensors='pt')

ex_outputs = dec_tokenizer.batch_encode_plus(
    ['rose ( 53 ) ; dog ( 38 ) ; help ( 7 ) AND theme ( 7 , 53 ) AND agent ( 7 , 38 )'], 
    return_tensors='pt')

"""Here is the forward method. For training, it is vital to have `labels=` here so that the model return a loss value."""

ex_rep = encdec(
    ex_inputs['input_ids'],
    ex_inputs['attention_mask'],
    ex_outputs['input_ids'],
    labels=ex_outputs['attention_mask'])

ex_rep.keys()

"""And here is how we will do generation:"""

ex_gen = encdec.generate(
    ex_inputs['input_ids'],
    attention_mask=ex_inputs['attention_mask'],
    max_new_tokens=512,
    eos_token_id=encdec.config.eos_token_id)

ex_gen

ex_pred = dec_tokenizer.batch_decode(
    ex_gen, 
    skip_special_tokens=False, 
    # Out tokenizer have this set already, but I am nervous:
    clean_up_tokenization_spaces=False)

ex_pred

"""### Model interface

Okay, finally, the main interface. If you do not plan to train your own models using our code, then you can treat `RecogsModel` as an interface and not worry about these details.
"""

from torch_model_base import TorchModelBase
import torch.nn as nn
from transformers import EncoderDecoderModel

"""As I mentioned above, Hugging Face `EncoderDecoderModel` instances will calculate a loss internally if you provide them with `labels`. Normally, one's optimization loop would need to do this manually. In order to rely on Hugging Face and still use the trainer in `torch_model_base.py`, we define this simple loss that just takes in model outputs and labels and returns `outputs.loss`. The labels argument is present for compatibility; it was already used internally to get the value of `outputs.loss` and so can be ignored."""

class RecogsLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.reduction = "mean"

    def forward(self, outputs, labels):
        """`labels` is ignored, as it was already used to assign a
        value of `outputs.loss`, and that value is all we need."""
        return outputs.loss

"""Here is a basic `nn.Module`. Its sole purpose is to organize the examples created by our `RecogsDataset` and feed them to the trained `EncoderDecoderModel`:"""

class RecogsModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.encdec = EncoderDecoderModel.from_pretrained(
            f"ReCOGS/ReCOGS-model")

    def forward(self, X_pad, X_mask, y_pad, y_mask, labels=None):
        outputs = self.encdec(
            input_ids=X_pad, 
            attention_mask=X_mask,
            decoder_attention_mask=y_mask,
            labels=y_pad)
        return outputs

"""And, at last, our interface. The keyword parameter `initialize=True` is the default because we are initially going to use this just for making predictions, and so we need the instance to establish all its parameters when we initialize it as opposed to waiting to do that when we call `fit` (which we may never do)."""

class RecogsModel(TorchModelBase):
    def __init__(self, *args,
            initialize=True,
            enc_vocab_filename=f"{SRC_DIRNAME}/src_vocab.txt",
            dec_vocab_filename=f"{SRC_DIRNAME}/tgt_vocab.txt",
            **kwargs):
        self.enc_vocab_filename = enc_vocab_filename
        self.dec_vocab_filename = dec_vocab_filename
        self.enc_tokenizer = get_tokenizer(self.enc_vocab_filename)
        self.dec_tokenizer = get_tokenizer(self.dec_vocab_filename)
        super().__init__(*args, **kwargs)
        self.loss = RecogsLoss()
        if initialize:
            self.initialize()

    def build_graph(self):
        return RecogsModule()

    def build_dataset(self, X, y=None):
        return RecogsDataset(
            self.enc_tokenizer, self.dec_tokenizer, X, y=y)

    def predict(self, X, device=None):
        device = self.device if device is None else torch.device(device)
        dataset = self.build_dataset(X)
        dataloader = self._build_dataloader(dataset, shuffle=False)
        self.model.to(device)
        self.model.eval()
        preds = []
        with torch.no_grad():
            for batch in dataloader:
                X_pad, X_mask = [x.to(device) for x in batch]
                outputs = self.model.encdec.generate(
                    X_pad,
                    attention_mask=X_mask,
                    max_new_tokens=512,
                    eos_token_id=self.model.encdec.config.eos_token_id)
                results = self.dec_tokenizer.batch_decode(
                    outputs, 
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=False)
                preds += results
        return preds

    def score(self, X, y, device=None):
        preds = self.predict(X, device=device)
        return recogs_exact_match(y, preds)

recogs_model = RecogsModel()

"""Predictions for our first to train cases"""

recogs_model.predict(dataset['dev'].input[: 2])

dataset['dev']

"""## Question 2: Exploring predictions [2 points]

Now that we are set up to use the model, we can move to Question 2. There is just one final preliminary: for ReCOGs, we want to come as close as possible to assessing systems purely on semantic criteria, as opposed to assessing their ability to predict arbitrary features of logical forms. In particular, we want predictions to be independent of the particular choice of variable names and independent of the order of conjuncts.

### ReCOGS assessment function

The function `recogs_exact_match` does this. It's a complex function, and so you can ignore its precise implementation details. Here are some illustrative examples to give you a feel for it:
"""

# The precise names of bound variables do not matter:

recogs_exact_match(
    "dog ( 4 ) AND happy ( 4 )", 
    "dog ( 7 ) AND happy ( 7 ) ")

# The order of conjuncts does not matter:

recogs_exact_match(
    "dog ( 4 ) AND happy ( 4 )", 
    "happy ( 7 ) AND dog ( 7 )")

# Consistency of variable names does matter:

recogs_exact_match(
    "dog ( 4 ) AND happy ( 4 )", 
    "dog ( 4 ) AND happy ( 7 )")

"""### Task

Your task is to write a utility function to see how well a model does on a specific generalization category in the generalization dataset. The metric is accuracy according to `recogs_exact_match`.
"""

def category_assess(gen_df, model, category):
    """Assess `model` against the `category` examples in `gen_df`.

    Parameters
    ----------
    gen_df: pd.DataFrame
        Should be `dataset["gen"]`
    model: A `RecogsModel instance
    category: str
        A string from `gen_df.category`

    Returns
    -------
    `pd.DataFrame` limited to `category` examples and with columns
    "prediction" and "correct" added by this function
    """
    # This line is done for you because of how important it is to
    # operate on a copy of the dataframe rather than the original!
    cat_df = gen_df[gen_df.category == category].copy()

    # Step 1: Add a column called "prediction" to `cat_df`. This should
    # give the predicted LFs:
    ##### YOUR CODE HERE
    cat_df["prediction"] = model.predict(cat_df.input)


    # Step 2: Add a column "correct" that says whether the prediction
    # and the gold output are the same. Must use `recogs_exact_match`.
    ##### YOUR CODE HERE
    cat_df["correct"] = cat_df.apply(
        lambda row: recogs_exact_match(row.output, row.prediction),
        axis=1
    )


    # Step 3: Return the `pd.DataFrame` `cat_df`:
    ##### YOUR CODE HERE
    return cat_df

def test_category_assess(func):
    testmod = RecogsModel()
    samp_df = dataset['gen'].head(150)
    examples = [
        ("active_to_passive", 0.80),
        ("unacc_to_transitive", 0.86),
        ("obj_to_subj_proper", 0.78)
    ]
    result_df = func(samp_df, testmod, "active_to_passive")
    if not isinstance(result_df, pd.DataFrame):
        print(f"Error `{func.__name__}`: "
              "Return value should be a `pd.DataFrame`")
        return
    errcount = 0
    for colname in ("input", "output", "category", "prediction", "correct"):
        if colname not in result_df.columns:
            errcount += 1
            print(f"Error `{func.__name__}`: column '{colname}' is missing")
    if errcount != 0:
        return
    expected_len = 5
    result_len = result_df.shape[0]
    if not result_df.shape[0] == expected_len:
        print(f"Error `{func.__name__}`: "
              f"Expected {expected_len} results, got {result_len}.")
        return
    errcount = 0
    for cat, expected in examples:
        result_df = func(samp_df, testmod, cat)
        result = result_df.correct.sum() / result_df.shape[0]
        result = round(result, 2)
        if result != expected:
            errcount += 1
            print(f"Error `{func.__name__}` with category {cat}: "
                  f"Expected acc {expected}, got {result}")
    if errcount == 0:
        print(f"No errors for `{func.__name__}`")

test_category_assess(category_assess)

"""Question 1 above might lead you to expect that our model will struggle with examples in which proper names appear with totally unfamiliar roles. For that question, you wrote `get_propername_role` to get `(name, role)` pairs from examples and `find_name_roles` to do analyses with that function. We can now run that same analysis on our errors:"""

gen_df = dataset['gen']

# Depending on your computer, this could take a while. On a relatively
# new Apple laptop, it took about 3 minutes. Colab will be much more
# variable in the time it takes, depending on what kind of instance
# you are running.

# pred_df = category_assess(gen_df, recogs_model, "obj_to_subj_proper")

"""Extract the errors:"""

# err_df = pred_df[pred_df.correct == False]

"""Use `find_name_roles` to get the role distribution in the error set:"""

# err_roles = find_name_roles(err_df)

# sorted(err_roles.items(), key=lambda x: len(x[1]))[: 3]

"""It's our old friend Charlie – in training, always a theme; in the generalization tests, always an agent.

## Question 3: In-context learning with DSP [2 points]

For this question, we are going to switch gears, from using our trained ReCOGS model to seeing whether we can get traction on this problem using only in-context learning. This question is meant to be very straightforward – our sole goal is to get you to the point where you have a working DSP program that you can build on.

### Set-up

Standard set-up for DSP, but we don't need a retriever:
"""

import cohere
from datasets import load_dataset
import openai
import os
import dsp

root_path = '.'

os.environ["DSP_NOTEBOOK_CACHEDIR"] = os.path.join(root_path, 'cache')

openai_key = os.getenv('OPENAI_API_KEY')  # or replace with your API key (optional)

cohere_key = 'NOvHZj1s5IKjdkBfqPTqB52oR5vuyzhY7yuK03HE'  # or replace with your API key (optional)

"""Our language model:"""

# Options for Cohere: command-medium-nightly, command-xlarge-nightly
lm = dsp.Cohere(model='command-xlarge-nightly', api_key=cohere_key)

# Options for OpenAI:
# [d["root"] for d in openai.Model.list()["data"]]
# lm = dsp.GPT3(model='text-davinci-001', api_key=openai_key)

"""DSP settings:"""

dsp.settings.configure(lm=lm)

"""### Train examples in DSP format

This will convert the train set into a list of `dsp.Example` instances to use for demonstrations:
"""

dsp_recogs_train = [dsp.Example(input=row['input'], output=row['output'])
                    for _, row in dataset['train'].iterrows()]

"""### Basic template"""

Input = dsp.Type(
    prefix="Input:", 
    desc="${the sentence to be translated}")

Output = dsp.Type(
    prefix="Output:", 
    desc="${a logical form}",
    format=dsp.format_answers)

cogs_template = dsp.Template(
    instructions="Translate sentences into logical forms.",
    input=Input(),
    output=Output())

"""Quick illustration:"""

ex = dsp.Example(
    input=dataset['train'].input[0],
    demos=dsp.sample(dsp_recogs_train, k=2))

print(cogs_template(ex))

dataset['train']

"""### Task

Your task is just to complete the following very basic DSP program. The steps are laid out for you:
"""

@dsp.transformation
def recogs_dsp(example, train=dsp_recogs_train, k=2): 
    # Step 1: Sample k train cases and add them to the `demos`
    # attribute of `example`:
    ##### YOUR CODE HERE
    example.demos = dsp.sample(train, k=k)



    # Run your program using `cogs_template`:
    ##### YOUR CODE HERE
    example, completions = dsp.generate(cogs_template)(example, stage='qa')


    # Return the `dsp.Completions`:
    ##### YOUR CODE HERE
    return completions

"""A quick test:"""

def test_recogs_dsp(func):
    k = 3
    ex = dsp.Example(input="Q0", output=["A0"])
    train = [
        dsp.Example(input="Q1", output=["A1"]),
        dsp.Example(input="Q2", output=["A2"]),
        dsp.Example(input="Q3", output=["A3"]),
        dsp.Example(input="Q4", output=["A4"])]
    compl = func(ex, train=train, k=k)
    errcount = 0
    # Check the LM was used as expected:
    if len(compl.data) != 1:
        errcount += 1
        print(f"Error for `{func.__name__}`: Unexpected LM output.")
    data = compl.data[0]
    # Check that the right number of demos was used:
    demos = data['demos']
    if len(demos) != k:
        errcount += 1
        print(f"Error for `{func.__name__}`: "
              f"Unexpected demo count: {len(demos)}")
    if errcount == 0:
        print(f"No errors found for `{func.__name__}`")

test_recogs_dsp(recogs_dsp)

recogs_dsp(ex).output

"""### Optional assessment

Here we sample 10 dev cases for a small evaluation. If you adapt this code, remember to use `recogs_exact_match` so that you aren't unfairly penalized for conjunct order or varible name differences.
"""

ssamp = dataset['dev'].sample(10)

ssamp['prediction'] = ssamp.input.apply(
    lambda x: recogs_dsp(dsp.Example(input=x)).output)

ssamp['correct'] = ssamp.apply(
    lambda row: recogs_exact_match(row['output'], row['prediction']), axis=1)

ssamp['correct'].sum() / ssamp.shape[0]

"""A random example to see what's going on:"""

ssamp.sample(1).to_dict(orient='records')

"""## Question 4: Original System [3 points]

For your original system, you can do anything at all. The only constraint (repeated from above):

__You cannot train your system on any examples from `dataset["gen"]`, nor can the output representations from those examples be included in any prompts used for in-context learning.__

In the cell below, please provide a brief technical description of your original system, so that the teaching team can gain an understanding of what it does. This will help us to understand your code and analyze all the submissions to identify patterns and strategies.
"""

# PLEASE MAKE SURE TO INCLUDE THE FOLLOWING BETWEEN THE START AND STOP COMMENTS:
#   1) Textual description of your system.
#   2) The code for your original system.
# PLEASE MAKE SURE NOT TO DELETE OR EDIT THE START AND STOP COMMENTS

# START COMMENT: Enter your system description in this cell.
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class T5BaseRecogsModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.encdec = AutoModelForSeq2SeqLM.from_pretrained("t5-base")

    def forward(self, X_pad, X_mask, y_pad, y_mask, labels=None):
        outputs = self.encdec(
            input_ids=X_pad, 
            attention_mask=X_mask,
            decoder_attention_mask=y_mask,
            labels=y_pad)
        return outputs

class T5BaseRecogsModel(RecogsModel):
    def __init__(self, *args, initialize=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enc_tokenizer = AutoTokenizer.from_pretrained("t5-base")
        self.dec_tokenizer = self.enc_tokenizer

    def build_graph(self):
        return T5BaseRecogsModule()

t5BaseModel = T5BaseRecogsModel(batch_size=5,
    gradient_accumulation_steps=20,
    max_iter=1, 
    early_stopping=True,
    n_iter_no_change=10,
    optimizer_class=torch.optim.Adam,
    eta=0.00001)

# STOP COMMENT: Please do not remove this comment.

_ = t5BaseModel.fit(dataset['train'].input[: 40], dataset['train'].output[: 40])

"""Assess"""

parameters = [0.00001]
accuracies = {}
for para in parameters:
    t5BaseModel = T5BaseRecogsModel(batch_size=5,
    gradient_accumulation_steps=20,
    max_iter=1, 
    early_stopping=True,
    n_iter_no_change=10,
    optimizer_class=torch.optim.Adam,
    eta=para)
    _ = t5BaseModel.fit(dataset['train'].input, dataset['train'].output)

    result_df = category_assess(dataset['dev'], t5BaseModel, 'in_distribution')
    acc = result_df.correct.sum() / result_df.shape[0]
    accuracies[para] = acc
    print(para, ' accuracy:', acc)
print(accuracies)


"""Here are some potential paths – just a few of many options, though!

### Option: DSP program

This could build on Question 3 very directly. All we have tried ourselves so far is the simple approach from that question.

### Option: Further training of our model

This is very easy to do. For example, here we do some training on the first 10 dev examples, and we've exposed some keyword arguments that may be of interest:
"""

# recogs_ff = RecogsModel(
#     batch_size=5,
#     gradient_accumulation_steps=20,
#     max_iter=100, 
#     early_stopping=True,
#     n_iter_no_change=10,
#     optimizer_class=torch.optim.Adam,
#     eta=0.00001)

# _ = recogs_ff.fit(dataset['dev'].input[: 40], dataset['dev'].output[: 40])

# """For this, you will want to pay a lot of attention to the optimization-related parameters.

# ### Option: Using a pretrained model

# The code used for Question 2 should make this very easy. For example, the following is the start of a complete solution using T5:
# """

# import torch.nn as nn
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# class T5RecogsModule(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.encdec = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

#     def forward(self, X_pad, X_mask, y_pad, y_mask, labels=None):
#         outputs = self.encdec(
#             input_ids=X_pad, 
#             attention_mask=X_mask,
#             decoder_attention_mask=y_mask,
#             labels=y_pad)
#         return outputs

# class T5RecogsModel(RecogsModel):
#     def __init__(self, *args, initialize=True, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.enc_tokenizer = AutoTokenizer.from_pretrained("t5-small")
#         self.dec_tokenizer = self.enc_tokenizer

#     def build_graph(self):
#         return T5RecogsModule()

# """This will make predictions, but they will be pretty totally disconnected from our task right now:"""

# t5mod = T5RecogsModel()

# t5_exs = dataset['dev'].input[: 2]

# t5_exs

# t5mod.predict(t5_exs)

# """This model needs to be fine-tuned on ReCOGS, which you can do with its `fit` method. In that case, you will want to pay a lot of attention to the optimization-related parameters to `TorchModelBase`.

# ### Option: Training a seq2seq model from scratch

# The above code for T5 is easily adapted to use a randomly initialized model. The config files used to train our core model are `encoder_config.json` and `decoder_config.json` in `SRC_DIRNAME`. These might be a good starting point in terms of parameters and other set-up details.

# ### There are lots more options!

# Maybe a symbolic solver? A learned semantic parser? Tree-structured neural network?

# ## Question 5: Bakeoff entry [1 point]

# Here we read in the bakeoff dataset:
# """

# bakeoff_df = pd.read_csv(
#     os.path.join(SRC_DIRNAME, "cs224u-recogs-test-unlabeled.tsv"), 
#     sep="\t", index_col=0)

# """For the bakeoff entry, you should add a column "prediction" containing your predicted LFs and then use the following command to write the file to disk:"""

# bakeoff_df.to_csv("cs224u-recogs-bakeoff-entry.tsv", sep="\t")

# """Here is what the first couple of lines of the file should look like:

# ```
# 	input	category	prediction
# 0	A cake was blessed by the wolf .	active_to_passive	PREDICTED LF
# 1	A melon was blessed by a boy .	active_to_passive	PREDICTED LF
# ```

# where `PREDICTED LF` is what you predicted. Here is a quick test you can run locally to ensure that the autograder won't fail:
# """

# def test_bakeoff_file(filename="cs224u-recogs-bakeoff-entry.tsv"):
#     ref_filename = os.path.join(SRC_DIRNAME, "cs224u-recogs-test-unlabeled.tsv")
#     ref_df = pd.read_csv(ref_filename, sep="\t", index_col=0)

#     entry_df = pd.read_csv(filename, sep="\t", index_col=0)

#     errcount = 0

#     # Check expected columns:
#     expected_cols = ["input", "category", "prediction"]
#     for col in expected_cols:
#         if col not in entry_df.columns:
#             errcount += 1
#             print(f"Missing column: {col}")
#     if errcount > 0:
#         return

#     # Use the "category" column as a check that the rows have not
#     # been shuffled:
#     if not entry_df.category.equals(ref_df.category):
#         errcount += 1
#         print("Rows do not seem to be aligned with reference file. "
#               "Might they have gotten shuffled?")

#     # Check that the predictions all have type str:
#     for line_num, x in enumerate(entry_df.prediction, start=1):
#         if not isinstance(x, str):
#             errcount += 1
#             print(f"Prediction on line {line_num} is not a str: {x}")

#     if errcount == 0:
#         print("Bakeoff file seems to be in good shape!")

# test_bakeoff_file()