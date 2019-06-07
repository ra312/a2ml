import click
from a2ml.api.a2ml import A2ML
from a2ml.api.utils.context import pass_context


@click.command('predict', short_help='Predict with deployed model.')
@click.argument('filename', required=True, type=click.STRING)
@click.option('--threshold', '-t', default=None, type=float,
    help='Threshold.')
@click.option('--model-id', '-m', type=click.STRING, required=False,
    help='Deployed model id.')
@click.option('--locally', is_flag=True, default=False,
    help='Predict locally using Docker image to run model.')
@pass_context
def cmdl(ctx, filename, model_id, threshold, locally):
    """Predict with deployed model."""
    ctx.setup_logger(format='')
    A2ML(ctx).predict(filename, model_id, threshold, locally)
