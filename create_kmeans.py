import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())


def main():
    for i in range(256):
        print(i)

    pass

    '''args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sa_root = os.getcwd()

    if args.output == '.':
        args.output = running_path

    if args.dot:
        #args.dot = running_path + '/' + args.dot
        create_project(sa_root, args.dot, args.copies, args.name, args.output)
        print('Project successfully created in %s/%s' % (args.output, args.name))
    else:
        msg = 'Missing parameters. Run create_project -h to see all parameters needed'
        raise Exception(msg)'''


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
