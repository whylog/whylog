runtime! debian.vim

" #########

function! Whylog()
	if !has('python')
		finish
	endif
	if !has("byte_offset")
		finish
	endif
python << EOF
import re


## VIM ##

import os.path
import vim

class OutputWindowContext(object):
	def __init__(self, gui):
		self.gui = gui
		self.origin_window_id = gui.get_current_window_id()
	def __enter__(self):
		self.gui.go_to_output_window()
		self.gui.set_window_writability(True)
		return vim.current.buffer
	def __exit__(self, type_, value, traceback):
		self.gui.set_window_writability(False)
		self.gui.go_to_window(self.origin_window_id)


class VimGUI(object): #(AbstractGUI):
	TEMPORARY_BUFFER_NAME = 'whylog_output'
	WINDOW_WRITEABILITY_STATE_DICT = {
		True: 'modifiable',
		False: 'nomodifiable',
	}
	def __init__(self):
		if not self._is_output_open():
			self._open_output_window()
		self.output_window_context = OutputWindowContext(self)

	def _get_output_window_id(self):
		for id_, window in enumerate(vim.windows):
			if window.buffer.name.endswith(os.path.join('', self.TEMPORARY_BUFFER_NAME)):
				return int(id_)+1
		return None

	def _get_output_buffer_id(self):
		for id_, buffer_ in enumerate(vim.buffers):
			if buffer_.name.endswith(os.path.join('', self.TEMPORARY_BUFFER_NAME)):
				return int(id_)
		return None

	def get_current_line(self):
		return vim.current.line

	def get_current_file_name(self):
		return vim.current.buffer.name

	def get_current_window_id(self):
		return int(vim.eval('winnr()'))

	def get_cursor_position(self):
		line = vim.current.line
		range_ = vim.current.range
		assert range_.start == range_.end
		return range_.start

	def _is_output_open(self):
		return self._get_output_buffer_id() is not None

	def go_to_window(self, id_):
		assert id_ is not None
		vim.command('%dwincmd w' % id_)

	def triggered_from_output_window(self):
		return self.get_current_window_id() == self._get_output_window_id()

	def _normal(self, command):
		vim.command("normal %s" % (command,))

	def _go_to_line(self, line):
		vim.command(':%d' % (line,))

	def _go_to_offset(self, byte_offset):
		vim.command(':go %d' % (byte_offset,))

	def go_to_output_window(self):
		self.go_to_window(self._get_output_window_id())

	def open_file_at_line(self, filename, line):
		vim.command(':edit %s' % (filename,))
		self._go_to_line(line)

	def _open_output_window(self):
		vim.command(':rightbelow split %s' % self.TEMPORARY_BUFFER_NAME)
		vim.command(':setlocal buftype=nowrite')
		vim.command(':resize 10')
		vim.command(':setlocal nomodifiable')
		vim.command(':wincmd k')

	def set_output(self, contents, line=None):
		with self.output_window_context as output_buffer:
			output_buffer[:] = contents.split('\n')
			if line is not None:
				self._go_to_line(line)

	def set_window_writability(self, state):
		vim.command(':setlocal %s' % self.WINDOW_WRITEABILITY_STATE_DICT[state])


def whylog(gui):
	filename = gui.get_current_file_name()
	cursor_position = gui.get_cursor_position()
	line = gui.get_current_line()
	# TODO: it's a mockup
	contents = """--- investigated item [node_1.log line 3]:
3 visible effect

--- has been caused by [node_1.log line 2]:
2 root cause
"""
	gui.set_output(contents, line=4)
	gui.go_to_output_window()
	return True

# "main()"

def get_gui_object():
	return VimGUI()

gui = get_gui_object()

if gui.triggered_from_output_window():
	# output window
	current_line = gui.get_current_line()
	if current_line.startswith('--- '):
		matcher = re.match('^--- .+ \[(.+) line (\d+)\]:$', current_line)
		assert matcher is not None, 'malformed line: %s' % (current_line,)
		vim.command(':wincmd k')  # FIXME should be "switch to input window"?
		gui.open_file_at_line(matcher.group(1), int(matcher.group(2)))
else:
	# normal (input) window
	success = whylog(gui)

EOF
endfunction

" vim-rest-console has good setup for keys
map <F2> :call Whylog()<CR>

