import pygame
import pyperclip


def handle_input_with_highlight(self, input_event) -> None:
    """
    Handles key-downs after a drag operation was finished and the highlighted area (drag) is still active.
    For arrow keys we merely jump to the destination.
    For other character-keys we remove the highlighted area and replace it (also over multiple lines)
    with the chosen letter.
    """
    # for readability & maintainability we use shorter variable names
    line_start = self.drag_chosen_LineIndex_start
    line_end = self.drag_chosen_LineIndex_end
    letter_start = self.drag_chosen_LetterIndex_start
    letter_end = self.drag_chosen_LetterIndex_end

    if self.dragged_finished and self.dragged_active:
        if input_event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT):
            # deselect highlight
            if input_event.key == pygame.K_DOWN:
                self.jump_to_end(line_start, line_end, letter_start, letter_end)
            elif input_event.key == pygame.K_UP:
                self.jump_to_start(line_start, line_end, letter_start, letter_end)
            elif input_event.key == pygame.K_RIGHT:
                self.jump_to_end(line_start, line_end, letter_start, letter_end)
            elif input_event.key == pygame.K_LEFT:
                self.jump_to_start(line_start, line_end, letter_start, letter_end)
            self.reset_after_highlight()

        elif input_event.key in (pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_CAPSLOCK, pygame.K_RCTRL, pygame.K_LCTRL):
            pass  # nothing happens, we wait for the second key with which it is being used in combination

        else:  # other key -> delete highlighted area and insert key (if not esc/delete)
            if line_start == line_end:  # delete in single line (no line-rearranging)
                if letter_start < letter_end:  # highlight from the left
                    self.delete_letter_to_letter(line_start, letter_start, letter_end)
                else:  # highlight from the right
                    self.delete_letter_to_letter(line_start, letter_end, letter_start)

            else:  # multi-line delete
                step = 1 if line_start < line_end else -1
                for i, line_number in enumerate(range(line_start, line_end + step, step)):
                    if i == 0:  # first line
                        if step > 0:  # downward highlighted
                            self.delete_letter_to_end(line_start, letter_start)  # delete right side from start
                        else:
                            self.delete_start_to_letter(line_start, letter_start)  # delete left side from start
                    elif i < len(range(line_start, line_end, 1)):  # middle line
                        self.delete_entire_line(line_start + 1)  # doesn't it always stay at line_start +1?
                    else:  # last line
                        if step > 0:
                            self.delete_start_to_letter(line_start + 1, letter_end)  # delete left side
                        else:
                            self.delete_letter_to_end(line_start + 1, letter_end)  # delete right side

                # join rest of start/end lines into new line in multiline delete
                l1 = self.line_String_array[line_start]
                l2 = self.line_String_array[line_start + 1]  # which was formerly line_end
                self.line_String_array[line_start] = l1 + l2
                self.delete_entire_line(line_start + 1)  # after copying contents, we need to delete

            # set caret and rerender line_numbers
            self.chosen_LineIndex = line_start if line_start <= line_end else line_end  # start for single_line
            self.chosen_LetterIndex = letter_start if line_start <= line_end else letter_end
            self.rerenderLineNumbers = True
            self.reset_after_highlight()
            self.deleteCounter = 1
            if input_event.key not in (pygame.K_DELETE, pygame.K_BACKSPACE):   # insert key unless delete/backaspace
                self.insert_unicode(input_event.unicode)


def handle_highlight_and_copy(self):
    """
    Copy highlighted String into clipboard if anything is highlighted, else no action.
    """
    copy_string = self.get_highlighted_characters()
    pyperclip.copy(copy_string)


def handle_highlight_and_paste(self):
    """
    Paste clipboard into cursor position.
    Replace highlighted area if highlight, else normal insert.
    """
    paste_string = pyperclip.paste()
    print("pressed: CTRL+V")


def handle_highlight_and_cut(self):
    """
    Copy highlighted String into clipboard if anything is highlighted, else no action.
    Delete highlighted part of the text.
    """
    pyperclip.copy("copy_string")
    print("pressed: CTRL+X")


def handle_highlight_and_h_all(self):
    """
    Highlight entire text.
    """
    self.set_drag_start_before_first_line()
    self.set_drag_end_after_last_line()
    self.update_caret_position_by_drag_end()
    self.dragged_finished = True
    self.dragged_active = True


def get_highlighted_characters(self) -> str:
    """
    Returns the highlighted characters (single- and multiple-line) from the editor (self.line_String_array)
    """
    if self.dragged_finished and self.dragged_active:
        letter_start = self.drag_chosen_LetterIndex_start
        letter_end = self.drag_chosen_LetterIndex_end

        if self.drag_chosen_LineIndex_start == self.drag_chosen_LineIndex_end:
            # single-line highlight
            return self.get_line_from_char_to_char(self.drag_chosen_LineIndex_start, letter_start, letter_end)

        else:  # multi-line highlight
            # set start and end in the correct order to append lines correctly
            if self.drag_chosen_LineIndex_start < self.drag_chosen_LineIndex_end:
                line_start = self.drag_chosen_LineIndex_start
                line_end = self.drag_chosen_LineIndex_end
            else:
                line_start = self.drag_chosen_LineIndex_end
                line_end = self.drag_chosen_LineIndex_start

            # loop through highlighted lines
            copied_chars = ""
            for i, line_index in enumerate(range(line_start, line_end+1)):
                if i == 0:  # first line
                    copied_chars = copied_chars + "\n" + self.get_line_from_char_to_end(line_index, letter_start)
                elif i < len(range(line_start, line_end)):  # middle line
                    copied_chars = copied_chars + "\n" + self.get_entire_line(line_index)
                else:  # last line
                    copied_chars = copied_chars + "\n" + self.get_line_from_start_to_char(line_index, letter_end)

            return copied_chars
    else:
        return ""


def get_entire_line(self, line_index) -> str:
    return self.line_String_array[line_index]


def get_line_from_start_to_char(self, line_index, char_index) -> str:
    return self.line_String_array[line_index][0:char_index]


def get_line_from_char_to_end(self, line_index, char_index) -> str:
    return self.line_String_array[line_index][char_index:]


def get_line_from_char_to_char(self, line_index, char1, char2) -> str:
    if char1 < char2:
        return self.line_String_array[line_index][char1:char2]
    else:
        return self.line_String_array[line_index][char2:char1]