__all__ = ['FootingRebuildMainWindow']


def __getattr__(name: str):
	if name == 'FootingRebuildMainWindow':
		from .main_window import FootingRebuildMainWindow as _FootingRebuildMainWindow

		return _FootingRebuildMainWindow
	raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
