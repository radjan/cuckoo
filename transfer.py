import sys
import click
from progressbar import ProgressBar, FormatLabel

import common


LOCAL = 'local'
FIREBASE = 'firebase'
OPTIONS = (LOCAL, FIREBASE)


@click.command()
@click.option('-f', '--read_from',
              prompt='Read from? (%s/%s)' % (LOCAL, FIREBASE))
@click.option('-t', '--save_to',
              prompt='Save to? (%s/%s)' % (LOCAL, FIREBASE))
def transfer(read_from, save_to):
    click.echo('%s --> %s' % (read_from, save_to))
    if read_from not in OPTIONS or save_to not in OPTIONS:
        print 'Should be %s or %s' % (LOCAL, FIREBASE)
        sys.exit(-1)
    if read_from == save_to:
        print 'Saving data to where it is from does not make sense.'
        sys.exit(-2)
    click.echo('This will OVERWRITE data in "%s". Are you sure? [y/N]'
               % save_to)
    confirm = sys.stdin.readline()
    if confirm.strip() != 'y':
        print 'byebye~'
        return

    common.READ_FROM = common.LOCAL if read_from == LOCAL else common.FIREBASE
    common.SAVE_TO = (common.LOCAL,)\
        if save_to == LOCAL else (common.FIREBASE,)

    print 'Transfering catalog...'
    catalog = common.load_catalog()
    common.save_catalog(catalog)

    print 'Transfering categories...'
    catalog = common.load_catalog()
    categories = common.load_categories()
    common.save_categories(categories)

    print 'Transfering state...'
    catalog = common.load_catalog()
    state = common.load_state()
    common.save_state(state)

    print 'Transfering filter results...'
    f_results = common.load_filter_results()
    common.save_filter_results(f_results)

    print 'Transfering indicator results...'
    i_results = common.load_indicator_results()
    common.save_indicator_results(i_results)

    print 'Transfering config...'
    config = common.load_config()
    common.save_config(config)

    todo = []
    for stocks in catalog.values():
        todo.extend(stocks)
    total = len(todo)
    print 'Transfering sotcks...'
    widgets = [FormatLabel('Processed: %(value)d / {0} (in: %(elapsed)s)'.
                           format(total))]
    pbar = ProgressBar(widgets=widgets, maxval=total)
    count = 0
    pbar.start()
    for s in todo:
        data = common.load_stock(s)
        common.save_stock(s, data)
        pbar.update(count)
        count += 1
    pbar.finish()


def load_errors():
    return _load_file(ERRORS, default=[])


def save_errors(data):
    _save_file(ERRORS, data)


if __name__ == '__main__':
    transfer()
