# Micronix Motor Controller Code

Originally found online from their website: https://micronixusa.com/page/support
This is all of their code. I made slight modification to their serial connection commands 
by adding reset_input_buffer and reset_out_buffer (basically buffer flushing) commands.

The MMC_PyLibrary.py library is used by my code to interact with the tunable filter. One can wish to write their own version of this as well 
given they understand the command structure (which is given in the pdf file in the parent directory).
