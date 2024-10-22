from typing import Any
from numpy import ndarray, ceil, zeros_like, zeros, hanning, arange, pad, dtype, floating, complexfloating, round
from numpy.fft import fft, ifft
from numpy._typing import _64Bit
from sounddevice import Stream, sleep


def phase_vocoder(
        input_data: ndarray,
        output: ndarray,
        status: int,
        shift_factor: float = 1.0
) -> None:
    """
    A phase vocoder implementation for real-time pitch shifting of audio.

    This function processes incoming audio data using the phase vocoder technique, allowing for
    dynamic pitch shifting based on the specified shift factor.

    :param input_data: Input audio data (1D array of float32).
    :param output: Output audio data (1D array of float32).
    :param status: Status of the audio stream (for error checking).
    :param shift_factor: Pitch shift factor (1.0 = no change, >1.0 = up, <1.0 = down).

    :raises ValueError: If `shift_factor` is not a positive number.
    :returns: None

    Future Configurations:
    - Implement real-time control of `shift_factor` through a GUI.
    - Add options for customizable FFT size and hop size.
    - Incorporate advanced error handling for robustness.
    - Enhance the algorithm for improved audio quality with better phase continuity.
    """
    if status:
        print(status)

    # Validate shift factor
    if shift_factor <= 0:
        raise ValueError("shift_factor must be a positive number.")

    # FFT parameters
    fft_size: int = 2048  # Size of the FFT window

    # Prepare the output array to be the same shape as the input
    output[:] = zeros_like(input_data)

    # Initialize variables for smoothing
    output_blend: ndarray[Any, dtype[floating[_64Bit]]] = zeros(fft_size)
    alpha: float = 0.5  # Blending factor for smoothing (0 < alpha < 1)

    # Process audio in chunks
    num_chunks: int = int(ceil(len(input_data) / (fft_size // 4)))
    i: int
    for i in range(num_chunks):
        start_index = i * (fft_size // 4)
        end_index = min(start_index + fft_size, len(input_data))
        frame = input_data[start_index:end_index] * hanning(fft_size)

        # Pad if necessary
        padded_frame = pad(frame, (0, fft_size - len(frame)), mode='constant')

        # Perform FFT
        fft_data: ndarray[Any, dtype[complexfloating[_64Bit, _64Bit]]] = fft(padded_frame)

        # Shift frequencies in the FFT data
        new_indices: ndarray[Any, dtype[int]] = round(arange(len(fft_data)).astype(float) * shift_factor).astype(int)
        new_indices = new_indices[new_indices < len(fft_data)]  # Prevent out-of-bounds
        shifted_fft: ndarray[Any, dtype[complex]] = zeros_like(fft_data, dtype=complex)
        shifted_fft[new_indices] = fft_data[:len(new_indices)]  # Apply the pitch shift

        # Smooth output using blending with previous output, and inverse FFT to convert back to time-domain signal
        output_blend = (1 - alpha) * output_blend + alpha * ifft(shifted_fft).real

        # Calculate the output start index and ensure it is within bounds
        out_start: int = int(start_index / shift_factor)

        if out_start < len(output):  # Check if out_start is within the bounds of output
            output[out_start:min(out_start + len(output_blend), len(output))] += output_blend[:len(output[out_start:])]


def main() -> None:
    """
    Main function.

    :return: None
    """
    # Set up the audio stream parameters
    input_samplerate: int = 48000  # Input sample rate
    block_size: int = 1024  # Number of frames per block

    # Create an audio stream with the phase vocoder as the callback
    with Stream(
            callback=phase_vocoder,
            samplerate=input_samplerate,
            blocksize=block_size,
            channels=1,
            dtype='float32',
    ):
        sleep(10000)  # Run the audio stream for 10 seconds


if __name__ == '__main__':
    main()
