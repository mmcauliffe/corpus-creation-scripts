import os
import re
import sys


def nonzero(a):
    return [i for i, e in enumerate(a) if e != 0]

def split(s, indices):
    return [s[i:j] for i,j in zip(indices, indices[1:]+[None])]

root_dir = r'D:\Data\speech\model_training_corpora\thai\globalphone_thai/files'
trl_root_dir = r'D:\Data\speech\model_training_corpora\thai\globalphone_thai/trl-unsegmented'
cleaned_dir = root_dir


word_set = set()
character_set = set()


for speaker_file in os.listdir(trl_root_dir):
    print(speaker_file)
    speaker = os.path.splitext(speaker_file)[0]
    utterances = {}
    current_utterance = 0
    speaker_folder = os.path.join(cleaned_dir, speaker)
    print(speaker_folder)
    os.makedirs(speaker_folder, exist_ok=True)
    trl_path = os.path.join(trl_root_dir, speaker_file)
    with open(trl_path, 'r', encoding='tis-620') as f:
        for line in f:
            print(line)
            line = line.strip()
            if not line:
                continue
            if 'SprecherID' in line:
                continue
            if line.startswith(';'):
                current_utterance += 1
                assert current_utterance == int(re.search(r'(\d+)', line).groups()[0])
                continue
            line = line.replace('\n', '')
            line = line.replace(' ', '')
            if current_utterance not in utterances:
                utterances[current_utterance] = ''
            utterances[current_utterance] += line
    for utt, text in utterances.items():
        utt_id = f"{speaker}_{utt}"
        output_path = os.path.join(speaker_folder, utt_id + '.lab')

        with open(output_path, 'w', encoding='utf8') as f:
            f.write(text)

err
with tf.Session() as session:
    model = tf.saved_model.loader.load(session, [tf.saved_model.tag_constants.SERVING], saved_model_path)
    signature = model.signature_def[tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
    graph = tf.get_default_graph()

    g_inputs = graph.get_tensor_by_name(signature.inputs['inputs'].name)
    g_lengths = graph.get_tensor_by_name(signature.inputs['lengths'].name)
    g_training = graph.get_tensor_by_name(signature.inputs['training'].name)
    g_outputs = graph.get_tensor_by_name(signature.outputs['outputs'].name)
    for speaker in os.listdir(root_dir):
        speaker_dir = os.path.join(root_dir, speaker)
        unsegmented_speaker_dir = os.path.join(cleaned_dir, speaker)
        os.makedirs(unsegmented_speaker_dir, exist_ok=True)
        for file in os.listdir(speaker_dir):
            if not file.endswith('.lab'):
                continue
            print(file)
            path = os.path.join(speaker_dir, file)
            unsegmented_path = os.path.join(unsegmented_speaker_dir, file)
            with open(path, 'r', encoding='utf8') as f:
                text = f.read().strip()
            words = text.split()
            text = ''.join(words)

            inputs = [ThaiWordSegmentLabeller.get_input_labels(text)]
            lengths = [len(text)]
            y = session.run(g_outputs, feed_dict={g_inputs: inputs, g_lengths: lengths, g_training: False})
            #print(text)
            new_words = []
            for w in split(text, nonzero(y)):
                new_words.append(w)
                #print(w)
            #print()
           #error
            with open(unsegmented_path, 'w', encoding='utf8') as f:
                f.write(' '.join(new_words))
            continue
            new_words = []
            for i, w in enumerate(words):
                if w in {',', '?'}:
                    continue
                if i > 0 and any(w.startswith(x) for x in questionable):
                    print(words[i-1], w, words[i-1]+w)
                    new_words[-1] += w
                else:
                    new_words.append(w)
                character_set.update(w)
            print(words)
            print(' '.join(words))
            print(''.join(words))
            print(new_words)
            print(' '.join(new_words))
            print(''.join(new_words))
            word_set.update(new_words)

print(word_set)
print(sorted(character_set))