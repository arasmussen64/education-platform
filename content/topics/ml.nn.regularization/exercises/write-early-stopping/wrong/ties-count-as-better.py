def early_stopping(val_losses, patience):
    """Walk the validation losses epoch by epoch (from 1): return the epoch with the lowest loss so far and the epoch at which training stops, which is the first one that is `patience` epochs past the best, or the last epoch if that never happens."""
    best_epoch, best = 1, val_losses[0]
    for epoch, value in enumerate(val_losses, start=1):
        if value <= best:
            best, best_epoch = value, epoch
        elif epoch - best_epoch >= patience:
            return best_epoch, epoch
    return best_epoch, len(val_losses)


print(early_stopping([0.9, 0.7, 0.6, 0.62, 0.61, 0.65, 0.7, 0.8], patience=3))
print(early_stopping([0.9, 0.7, 0.6, 0.5, 0.4], patience=3))
print(early_stopping([0.5, 0.5, 0.5, 0.5], patience=2))
