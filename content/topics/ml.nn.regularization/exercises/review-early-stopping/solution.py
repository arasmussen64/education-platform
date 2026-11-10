def early_stopping(val_losses, patience):
    """The epoch (from 1) with the lowest loss so far, and the epoch at which training stops: patience epochs past the best, or the last."""
    best_epoch, best = 1, val_losses[0]
    for epoch, value in enumerate(val_losses, start=1):
        if value < best:
            best, best_epoch = value, epoch
        elif epoch - best_epoch >= patience:
            return best_epoch, epoch
    return best_epoch, len(val_losses)


print(early_stopping([1.0, 0.8, 0.7, 0.75, 0.74, 0.76, 0.77, 0.9], patience=4))
print(early_stopping([1.0, 0.9, 0.8], patience=4))
