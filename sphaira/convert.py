import argparse
import projection as proj


def main():
    parser = argparse.ArgumentParser(
        prog='convert',
        description='Sphaira converter for spherical data.',
    )
    parser.add_argument('-i', '--in_format', help='IN_FORMAT')
    parser.add_argument('input', help='INPUT')
    parser.add_argument('-o', '--out_format', help='OUT_FORMAT', required=True)
    parser.add_argument('output', help='OUTPUT')
    args = parser.parse_args()
    in_format = proj.get_format(args.in_format)
    out_format = proj.get_format(args.out_format)
    assert out_format is not None
    sphere = proj.load_sphere(args.input, projection=in_format)
    in_format = sphere.__class__
    print('Loaded input %s from %s.' % (in_format.__name__, args.input))
    sphere = proj.convert_sphere(sphere, out_format)
    print('Converted %s to %s.' % (in_format.__name__, out_format.__name__))
    proj.save_sphere(args.output, sphere)
    print('Saved output %s into %s.' % (out_format.__name__, args.output))


if __name__ == '__main__':
    main()
