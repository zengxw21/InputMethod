from predict import Binary, Ternary
from tqdm import tqdm
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='../dataset/input.txt')
    parser.add_argument('--output', '-o', default='../dataset/output.txt')
    parser.add_argument('--answer', '-a', default='../dataset/std_output.txt')
    parser.add_argument('--model',
                        '-m',
                        default='Ternary',
                        choices=['Binary', 'Ternary'])
    args = parser.parse_args()

    ModelName = eval(args.model)
    model = ModelName()
    input_path = args.input
    output_path = args.output
    ans_path = args.answer
    with open(output_path, 'w', encoding='utf8') as output:
        with open(input_path, 'r', encoding='utf8') as input:
            sentences = input.readlines()
        output_sentences = []
        for sentence in tqdm(sentences):
            res = model.forward(sentence.strip())
            output.write(res + '\n')
            output_sentences.append(res)
        try:
            with open(ans_path, 'r', encoding='utf8') as ans:
                ans_sentences = ans.readlines()
            cnt = 0
            sum = 0
            per_sum = 0
            for i in tqdm(range(len(sentences))):
                if output_sentences[i] == ans_sentences[i].strip():
                    cnt += 1
                for j in range(len(output_sentences[i])):
                    if output_sentences[i][j] == ans_sentences[i][j]:
                        per_sum += 1
                sum += len(output_sentences[i])
            print('句正确率', str(int(cnt / len(sentences) * 10000) / 100) + '%')
            print('字正确率', str(int(per_sum / sum * 10000) / 100) + '%')
        except Exception as e:
            print(e)
